# -*- coding: utf-8 -*-
#
# INVENIO-SIP2
# Copyright (C) 2020 UCLouvain
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Invenio-SIP2 socket server management."""

import selectors
import signal
import socket

from flask import current_app

from .api import Message
from .errors import InvalidSelfCheckMessageError
from .ext import logger
from .proxies import current_sip2
from .records.record import Client, Server


class SocketServer:
    """Socket server."""

    selector = selectors.DefaultSelector()

    def __init__(self, name, host='0.0.0.0', port=3004, **kwargs):
        """Constructor."""
        self.server_name = name
        self.host = host
        self.port = port
        self.remote_app = kwargs.pop('remote')
        self.process_id = kwargs.pop('process_id')
        self.server = Server.create(data=vars(self))
        self.server['process_id'] = self.process_id
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen()
        logger.info('listening on {host}, {port}'.format(
            port=self.port,
            host=self.host
        ))
        signal.signal(signal.SIGINT, self.handler_stop_signals)
        signal.signal(signal.SIGTERM, self.handler_stop_signals)
        sock.setblocking(False)
        self.selector.register(
            sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=None)

    def run(self):
        """Run socket server."""
        try:
            self.server.up()
            while True:
                events = self.selector.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                        except Exception as ex:
                            logger.error(
                                f'message cannot be processed: {ex}',
                            )
                            message.close()
        except Exception as e:
            logger.error(
                'SIP2 server closed prematurely ({host}, {port}: {msg}'.format(
                    port=self.port,
                    host=self.host,
                    msg=e
                )
            )
        finally:
            self.close()

    def accept_wrapper(self, sock):
        """Accept connection wrapper."""
        connection, address = sock.accept()  # Should be ready to read
        logger.info('accepted connection from {address}'.format(
            address=address
        ))
        connection.setblocking(False)

        message = SocketEventListener(
            self.server, self.selector, connection, address)
        self.selector.register(connection, selectors.EVENT_READ, data=message)

    def close(self):
        """Close socket server."""
        try:
            self.selector.close()
        except:
            pass
        self.server.down()

    def handler_stop_signals(self, signum, frame):
        """Handle stop signals."""
        self.close()


class SocketEventListener:
    """Socket event listener class."""

    sock = None

    def __init__(self, server, selector, sock, addr):
        """Constructor."""
        self.server = server
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b''
        self._send_buffer = b''
        self.request = None
        self.response = None
        self.message = None
        self.response_created = False
        self.error_detection = current_app.config.get('SIP2_ERROR_DETECTION')
        self.line_terminator = current_app.config.get('SIP2_LINE_TERMINATOR')
        self.message_encoding = current_app.config.get('SIP2_TEXT_ENCODING')
        self.client = Client.create(data=self.dumps())

    def dumps(self):
        """Dumps record."""
        data = {
            'server': {
                'id': self.server.id
            },
            'ip_address': self.addr[0],
            'socket': self.addr[1],
        }
        if self.request:
            data['last_request'] = self.request.dumps()
        if self.response:
            data['last_response'] = self.response.dumps()
        return data

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == 'r':
            events = selectors.EVENT_READ
        elif mode == 'w':
            events = selectors.EVENT_WRITE
        elif mode == 'rw':
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        """Read request from the selfcheck client."""
        try:
            # Should be ready to read
            data = self.sock.recv(1024)
            # strip the line separator
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                request = data.decode(encoding=self.message_encoding)
                # strip the line separator
                request = \
                    request[:len(request) - len(self.line_terminator)]
                self.request = Message(request=request)
                if self.validate_message(request):
                    self._recv_buffer += data
                else:
                    raise InvalidSelfCheckMessageError(
                        'invalid checksum for {message}'.format(
                            message=self.request.dumps()
                        ))
                    self.close()
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        """Send message to the selfcheck client."""
        if self._send_buffer:
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
        self.response_created = False
        self._set_selector_events_mask("r")

    def _create_message(self):
        """Create response message that will be send to selfcheck client."""
        response_text = str(self.response)
        if self.error_detection:
            # if the current request is a request resend message, we don't
            # return the sequence number
            if self.request.command != '97':
                response_text += 'AY'
                response_text += self.request.sequence_number
            response_text += 'AZ'
            response_text += self.calculate_checksum(response_text)
        else:
            # remove last character `|` if exist
            response_text.rstrip("|")
        response_text += self.line_terminator

        return bytes(response_text, self.message_encoding)

    def process_events(self, mask):
        """Process events with the selfcheck client."""
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        """Read message from selfcheck client."""
        self._read()
        if self._recv_buffer:
            message = 'request from {terminal} ({ip}) : {request}'.format(
                terminal=self.client.terminal,
                ip=self.client.get('ip_address'),
                request=self.request.dumps(),
            )
            logger.info('{message}'.format(
                message=message
            ))
            self.process_request()

    def write(self):
        """Send response to selfcheck client."""
        if self.request:
            if not self.response_created:
                self.create_response()
            message = 'send to {terminal} ({ip}): {response}'.format(
                terminal=self.client.terminal,
                ip=self.client.get('ip_address'),
                response=self.response.dumps()
            )
            logger.info('{message}'.format(
                message=message
            ))
            self._write()

    def close(self):
        """Close the connection with selfcheck client."""
        logger.info('closing connection to {address}'.format(
            address=self.addr
        ))
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            current_app.logger.error(
                'error: selector unregistered for {terminal}:{terminal_ip} '
                'on {server}'.format(
                    terminal=self.client.terminal,
                    terminal_ip=self.client.get('ip_address'),
                    server=self.server.get('server_name')
                ), e
            )
        try:
            self.sock.close()
        except OSError as e:
            current_app.logger.error(
                'error: socket closing exception for {terminal}:{terminal_ip} '
                'on {server}'.format(
                    terminal=self.client.terminal,
                    terminal_ip=self.client.get('ip_address'),
                    server=self.server.get('server_name')
                )
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None
            self.client.delete()

    def process_request(self):
        """Processing of selfcheck message."""
        self.response = current_sip2.sip2.execute(
            self.request,
            client=self.client
        )
        if not self.response:
            self.response = '96'
        if self.request.command is not '97':
            self.client.update(self.dumps())

        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask("w")

    def create_response(self):
        """Create response message."""
        if self.request:
            message = self._create_message()
            self.response_created = True
            self._send_buffer += message

    def calculate_checksum(self, message):
        """Generate and format checksums for SIP2 messages."""
        # Calculate CRC
        checksum = 0
        for n in range(0, len(message)):
            checksum = checksum + ord(message[n:n + 1])
        crc = format((-checksum & 0xFFFF), 'X')
        return crc

    def validate_message(self, request):
        """Validate sequence number and checksum."""
        # check for enabled crc
        if not self.error_detection:
            return True

        return self.verify_sequence_number(request) and \
            self.verify_checksum(request)

    def verify_checksum(self, message):
        """Verify the integrity of SIP2 messages containing checksum."""
        # get four last characters
        test = message[-4:]
        # check validity
        return len(test) > 1 and \
            (self.calculate_checksum(test[0]) > test[1] and
                self.calculate_checksum(test[0]) < test[1]) == 0

    def verify_sequence_number(self, message):
        """Check sequence number increment."""
        if not self.client.last_request_message \
                or self.request.command is '97':
            return True

        # get current sequence from tag AY
        sequence = message[-7:-6]
        # get sequence number from last request message
        last_sequence_number = self.client.get_last_sequence_number

        return last_sequence_number and \
            (int(sequence)-1 == int(last_sequence_number) or
                (int(last_sequence_number) == 9 and int(sequence) == 0))
