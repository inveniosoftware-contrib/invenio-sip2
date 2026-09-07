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

import os
import socket
from unittest.mock import patch

import psutil
import pytest

from invenio_sip2.datastore import Datastore, Sip2RedisDatastore
from invenio_sip2.errors import ServerAlreadyRunning
from invenio_sip2.records.record import Client, Server

#: A pid high enough that no process can be holding it.
DEAD_PID = 2**22


def registration(**overrides):
    """Build what `SocketServer` writes when it registers itself."""
    data = {
        "server_name": "reclaim_server",
        "host": "0.0.0.0",
        "port": 3010,
        "remote_app": "test_ils",
        "hostname": socket.gethostname(),
        "process_id": os.getpid(),
    }
    data.update(overrides)
    return data


@patch.multiple(Datastore, __abstractmethods__=set())
def test_datastore_interface(app, server_data):
    """Test datastore interface."""
    ds = Datastore()
    with pytest.raises(NotImplementedError):
        ds.add("key", "value")
    with pytest.raises(NotImplementedError):
        ds.get("id_")
    with pytest.raises(NotImplementedError):
        ds.update("key", "value")
    with pytest.raises(NotImplementedError):
        ds.delete("key")
    with pytest.raises(NotImplementedError):
        ds.all()
    with pytest.raises(NotImplementedError):
        ds.search("query")
    with pytest.raises(NotImplementedError):
        ds.flush()


def test_redis_datastore(app, server_data):
    """Redis datastore tests"""
    with app.app_context():
        datastore = Sip2RedisDatastore(app)
        # clear datastore
        datastore.flush()
        server = Server(server_data)
        datastore.add(server, "key_1")
        data = datastore.get(server.id, "server")
        assert data
        datastore.flush()
        assert not datastore.get(server.id)


def test_record_metadata(app, server_data, dummy_client_data):
    """Record metadata tests"""
    with app.app_context():
        server = Server.create(server_data, id_="key_1")
        assert server.id
        assert server.count() == 1
        data = Server.find_server(server_name=server_data.get("server_name"))
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
        assert Server.get_record_by_id("nonexistent_id") is None
        assert Server.find_server(server_name="nonexistent_server") is None
        server.delete()


def test_server_is_alive(app):
    """A `running` status is only trusted while its owner still exists."""
    with app.app_context():
        Sip2RedisDatastore(app).flush()
        # An owner that cannot be identified gets the benefit of the doubt,
        # so registrations written before hostnames were recorded still work.
        server = Server.create({"server_name": "anonymous_owner"})
        assert server.is_alive

        server = Server.create(registration())
        server.up()
        # Owned by this very process.
        assert server.is_alive

        # Same pid, but written by another machine or a previous container:
        # the pid means nothing here.
        server["hostname"] = "a-container-that-is-gone"
        assert not server.is_alive

        # This machine, but the process is gone.
        server["hostname"] = socket.gethostname()
        server["process_id"] = DEAD_PID
        assert not psutil.pid_exists(DEAD_PID)
        assert not server.is_alive

        # A pid recycled after a reboot points at a process that cannot
        # predate the registration it would be answering for.
        server["process_id"] = os.getpid()
        server["started_at"] = "2000-01-01T00:00:00+00:00"
        assert not server.is_alive


def test_server_is_alive_without_hostname(app):
    """Registrations written before hostnames were recorded still resolve.

    The upgrade that introduced hostnames must not strand the registration it
    finds in the datastore, or every restart keeps failing exactly as before.
    """
    with app.app_context():
        Sip2RedisDatastore(app).flush()
        legacy = Server.create(registration())
        del legacy["hostname"]
        legacy.up()
        # Still running here, so still protected.
        assert legacy.is_alive
        # Left behind by a process that is gone: reclaimable.
        legacy["process_id"] = DEAD_PID
        assert not legacy.is_alive


def test_create_reclaims_a_stale_registration(app):
    """A server killed without deregistering can be started again."""
    with app.app_context():
        Sip2RedisDatastore(app).flush()
        killed = Server.create(registration(process_id=DEAD_PID))
        killed.up()
        # Exactly the state a SIGKILL leaves behind.
        assert killed.is_running
        assert not killed.is_alive

        reclaimed = Server.create(registration())
        # Same registration, handed over to the process starting now.
        assert reclaimed.id == killed.id
        assert Server.count() == 1
        assert reclaimed.get("process_id") == os.getpid()
        assert not reclaimed.is_running


def test_create_refuses_a_live_registration(app):
    """A server that is genuinely running is still protected."""
    with app.app_context():
        Sip2RedisDatastore(app).flush()
        server = Server.create(registration())
        server.up()

        with pytest.raises(ServerAlreadyRunning):
            Server.create(registration())

        # ...unless the takeover is explicit.
        reclaimed = Server.create(registration(), force=True)
        assert reclaimed.id == server.id
        assert Server.count() == 1


def test_find_server_ignores_the_owner(app):
    """A restart must recognise its own record under a new pid and host."""
    with app.app_context():
        Sip2RedisDatastore(app).flush()
        server = Server.create(registration())
        found = Server.find_server(
            **registration(process_id=DEAD_PID, hostname="somewhere-else")
        )
        assert found is not None
        assert found.id == server.id
