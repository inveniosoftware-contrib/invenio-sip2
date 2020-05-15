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

"""Socket server test."""

from __future__ import absolute_import, print_function

import socket


def test_socket_server(dummy_socket_server):
    """Test socket server."""

    # This is fake test client to attempt a connect and disconnect
    fake_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fake_client.settimeout(1)
    fake_client.connect(('127.0.0.1', 3005))
    fake_client.close()
