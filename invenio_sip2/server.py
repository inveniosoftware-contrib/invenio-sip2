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


import contextlib
import logging
import selectors
import signal
import socket

from flask import current_app

from invenio_sip2.api import Message
from invenio_sip2.errors import CommandNotFound
from invenio_sip2.proxies import current_logger as logger
from invenio_sip2.proxies import current_sip2
from invenio_sip2.records import Client, Server
from invenio_sip2.utils import verify_checksum, verify_sequence_number


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
                        except (UnicodeDecodeError, CommandNotFound) as err:
                            logger.debug(
                                err,
                                exc_info=True
                            )
                            message.close()
                        except RuntimeError as e:
                            logger.debug(
                                f'message cannot be processed: {e}',
                                exc_info=True
                            )
                            message.close()
                        except Exception as ex:
                            logger.error(
                                f'message cannot be processed: {ex}',
                                exc_info=True
                            )
                            message.close()
        except Exception as e:
            logger.error(
                'SIP2 server closed prematurely ({host}, {port}: {msg}'.format(
                    port=self.port,
                    host=self.host,
                    msg=e
                ),
                exc_info=True
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
        with contextlib.suppress(Exception):
            self.selector.close()
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
        self.error_detection = current_sip2.is_error_detection_enabled
        self.line_terminator = current_sip2.line_terminator
        self.message_encoding = current_sip2.text_encoding
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
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                log_prefix = f'request from {self.client.terminal} ' \
                    f'({self.client.get("ip_address")}, ' \
                    f'{self.client.get("socket")})'
                request_msg = data.decode(encoding=self.message_encoding)
                # strip the line terminator
                request_msg = \
                    request_msg[:len(request_msg) - len(self.line_terminator)]
                try:
                    self.request = Message(request=request_msg)
                    request = self.request.dumps() if logger.level == \
                        logging.DEBUG else request_msg

                    logger.info(f'{log_prefix}: {request}')

                    if self.validate_message(request_msg):
                        self._recv_buffer += data
                    else:
                        logger.error(
                            f'invalid checksum for: {request_msg}',
                            exc_info=True
                        )
                        # prepare request selcheck resend message
                        self.response = Message(
                            message_type=current_sip2.sip2_message_types
                            .get_by_command('96')
                        )
                        # Set selector to listen for write events
                        self._set_selector_events_mask("w")
                except CommandNotFound as e:
                    raise CommandNotFound(
                        message=f'{log_prefix} - {e.description}')
                except Exception as err:
                    logger.info('{log_prefix} - {request_msg}')
                    raise Exception(err)
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
            self.process_request()

    def write(self):
        """Send response to selfcheck client."""
        if self.request:
            if not self.response_created:
                self.create_response()

            if self.response and logger.level in [logging.DEBUG]:
                response = self.response.dumps()
            else:
                response = str(self.response)
            logger.info(f'send to {self.client.terminal} '
                        f'({self.client.get("ip_address")}, '
                        f'{self.client.get("socket")}): {response}')
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
        if self.request.command != '97':
            self.client.update(self.dumps())

        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask("w")

    def create_response(self):
        """Create response message."""
        if self.request:
            message = bytes(str(self.response), self.message_encoding)
            self.response_created = True
            self._send_buffer += message

    def validate_message(self, request_msg):
        """Validate sequence number and checksum for request message."""
        # check for enabled crc
        if not self.error_detection:
            if self.request.sequence_number and self.request.checksum:
                logger.warning(
                    'error detection is disabled but the request message '
                    'contains sequence number and checksum: {message}'.format(
                        message=self.request
                    ))
            return True
        if self.request.checksum:
            return True \
                if self.request.command == '97' \
                else verify_sequence_number(self.client, self.request) \
                and verify_checksum(request_msg)

        logger.warning(
            'error detection is enabled but the request message '
            'hasn\'t checksum: {message}'.format(
                message=self.request))
        return True
