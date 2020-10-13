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

"""Server test."""

from __future__ import absolute_import, print_function

import socket
import threading

from invenio_sip2.server import SocketServer


def test_socket_server(selfckeck_login_message):
    """Test socket server"""
    # start socket server in a background thread
    server = SocketServer(host='127.0.0.1', port=3005, remote='test')
    server_thread = threading.Thread(target=server.run)
    server_thread.start()

    # test client connection
    client = socket.socket()
    client.connect(('127.0.0.1', 3005))
    client.settimeout(1)
    client.sendall(selfckeck_login_message)
    client.close()

    # Make sure server thread finishes
    server_thread.join()
