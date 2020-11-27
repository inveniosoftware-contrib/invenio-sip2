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

import re
import selectors
import signal
import socket
import traceback

from flask import current_app

from .api import Message
from .errors import InvalidSelfCheckMessageError
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
        self.server = Server.create(data=vars(self))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen()
        # TODO : use another logging method
        print("listening on", (self.host, self.port))
        signal.signal(signal.SIGINT, self.handler_stop_signals)
        signal.signal(signal.SIGTERM, self.handler_stop_signals)
        sock.setblocking(False)
        self.selector.register(
            sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=None)

    def run(self):
        """Run socket server."""
        try:
            # TODO: add class for server state?
            self.server['status'] = 'running'
            self.server.update(self.server)
            while True:
                events = self.selector.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                        except Exception:
                            print(
                                "main: error: exception for",
                                f"{message.addr}:\n{traceback.format_exc()}",
                            )
                            message.close()
        except KeyboardInterrupt:
            # TODO : use another logging method
            print("caught keyboard interrupt, exiting")
        finally:
            self.close()
            raise RuntimeError("Server closed.")

    def accept_wrapper(self, sock):
        """Accept connection wrapper."""
        connection, address = sock.accept()  # Should be ready to read
        # TODO : use another logging method
        print("accepted connection from", address)
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
        self.server['status'] = 'down'
        self.server.update(self.server)

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
        self.with_checksum = current_app.config.get('SIP2_CHECKSUM_CONTROL')
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
                if self.verify_checksum(request):
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
        if self.with_checksum:
            response_text += 'AZ'
            response_text += self.calculate_checksum(response_text)

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
            message = 'request: {request} to {client}'.format(
                request=str(self.request),
                client=self.client
            )
            # TODO : use another logging method
            print(message)
            self.process_request()

    def write(self):
        """Send response to selfcheck client."""
        if self.request:
            if not self.response_created:
                self.create_response()
            message = 'send: {response} to {client}'.format(
                response=str(self.response),
                client=self.client
            )
            # TODO : use another logging method
            print(message)
            self._write()

    def close(self):
        """Close the connection with selfcheck client."""
        # TODO : use another logging method
        print("closing connection to", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                f"error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except OSError as e:
            # TODO : use another logging method
            print(
                f"error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None
            self.client.delete()

    def process_request(self):
        """Processing of selfcheck message."""
        # request_message = Message(request=self.request)
        self.response = current_sip2.sip2.execute(
            self.request,
            client=self.client
        )
        if not self.response:
            self.response = '96'
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

    def verify_checksum(self, message):
        """Verify the integrity of SIP2 messages containing checksum."""
        # check for enabled crc
        if not self.with_checksum:
            return True

        # test the received message's CRC by generating our own CRC
        test = re.split('(.{4})', message.strip())

        # check validity
        return len(test) > 1 and \
            (self.calculate_checksum(test[0]) > test[1] and
                self.calculate_checksum(test[0]) < test[1]) == 0
