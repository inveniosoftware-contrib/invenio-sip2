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

import socket
from unittest.mock import MagicMock

import pytest

from invenio_sip2.server import SocketEventListener


def test_set_selector_events_mask_invalid_mode():
    """Test _set_selector_events_mask raises ValueError for invalid mode."""
    listener = object.__new__(SocketEventListener)
    listener.selector = MagicMock()
    listener.sock = MagicMock()
    with pytest.raises(ValueError, match="Invalid events mask mode"):
        listener._set_selector_events_mask("invalid")  # noqa: SLF001


@pytest.mark.skip(reason="Remove this when github actions problem is fixed")
def test_socket_server(app, dummy_socket_server, selfckeck_login_message):
    """Test socket server"""
    with app.app_context():
        # test client connection
        client = socket.socket()
        client.connect(("127.0.0.1", 3006))
        client.settimeout(1)
        client.sendall(selfckeck_login_message)
        client.close()
