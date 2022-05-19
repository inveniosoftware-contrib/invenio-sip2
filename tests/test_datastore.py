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

"""Invenio-sip2 datastore test."""

from __future__ import absolute_import, print_function

from unittest.mock import patch

import pytest

from invenio_sip2.datastore import Datastore, Sip2RedisDatastore
from invenio_sip2.errors import ServerAlreadyRunning
from invenio_sip2.records.record import Client, Server


@patch.multiple(Datastore, __abstractmethods__=set())
def test_datastore_interface(app, server_data):
    """Test datastore interface."""
    ds = Datastore()
    with pytest.raises(NotImplementedError):
        ds.add('key', 'value')
    with pytest.raises(NotImplementedError):
        ds.get('id_')
    with pytest.raises(NotImplementedError):
        ds.update('key', 'value')
    with pytest.raises(NotImplementedError):
        ds.delete('key')
    with pytest.raises(NotImplementedError):
        ds.all()
    with pytest.raises(NotImplementedError):
        ds.search('query')
    with pytest.raises(NotImplementedError):
        ds.flush()


def test_redis_datastore(app, server_data):
    """Redis datastore tests"""
    with app.app_context():
        datastore = Sip2RedisDatastore(app)
        # clear datastore
        datastore.flush()
        server = Server(server_data)
        datastore.add(server, 'key_1')
        data = datastore.get(server.id, 'server')
        assert data
        datastore.flush()
        assert not datastore.get(server.id)


def test_record_metadata(app, server_data, dummy_client_data):
    """Record metadata tests"""
    with app.app_context():
        server = Server.create(server_data, id_='key_1')
        assert server.id
        assert server.count() == 1
        data = Server.find_server(server_name=server_data.get('server_name'))
        assert data.id == server.id
        assert not server.is_running
        server.up()
        assert server.is_running
        # create client
        client = Client.create(dummy_client_data)
        assert client.id
        # test empty value
        assert not client.library_language
        assert not client.last_response_message
        assert not client.last_request_message
        assert not client.last_sequence_number
        # try to clear empty patron session
        client.clear_patron_session()
        # try to recreate same server
        with pytest.raises(ServerAlreadyRunning):
            Server.create(server_data)
        server.down()
        assert not server.is_running
        server.delete()
