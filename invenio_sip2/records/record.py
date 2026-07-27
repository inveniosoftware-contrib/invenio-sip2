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

"""API for manipulating the client."""

import contextlib
import socket
from copy import deepcopy
from datetime import UTC, datetime
from uuid import uuid4

import psutil

from invenio_sip2 import current_datastore as datastore
from invenio_sip2.errors import ServerAlreadyRunning
from invenio_sip2.proxies import current_logger as logger

#: Fields describing the process that holds a server registration rather than
#: the server itself. They must stay out of lookups, otherwise a restart under
#: a new pid or in a new container would fail to recognise its own record and
#: register a duplicate.
SERVER_OWNER_KEYS = ("process_id", "hostname")


class Sip2RecordMetadata(dict):
    """Sip2RecordMetadata class."""

    record_type = None

    def __init__(self, data, **kwargs):
        """Initialize instance with dictionary data.

        :param data: Dict with record metadata.
        """
        super().__init__(data or {})

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        """Create record.

        :param data: Dict with metadata.
        :param id_: Specify a UUID to use for the new record.
        """
        if not cls.record_type:
            msg = f"{cls.__name__} must define a record_type"
            raise ValueError(msg)
        # TODO: check if record already exist and raise exception
        id_ = id_ or str(uuid4())

        data["id"] = id_
        record = cls(data, **kwargs)
        record["created"] = datetime.now(UTC).isoformat()
        datastore.add(record, id_=id_, **kwargs)

        return record

    @property
    def id(self):
        """Shortcut for id."""
        return self.get("id", None)

    def get_key(self):
        """Get generated key for Sip2RecordMetadata object."""
        return f"{self.record_type}:{self.id}"

    def update(self, data):
        """Update instance with dictionary data.

        :param data: Dict with metadata.
        """
        if self.id:
            super().update(data)
            data["updated"] = datetime.now(UTC).isoformat()
            datastore.update(self)

    def delete(self):
        """Delete record by uuid."""
        datastore.delete(self)

    def search(self, query="*", index_type=None, filter_query=None):
        """Search record by query."""
        return datastore.search(query, index_type=index_type, filter_query=filter_query)

    @classmethod
    def get_record_by_id(cls, id_):
        """Get record by uuid."""
        data = datastore.get(id_, cls.record_type)
        if data:
            return cls(data)
        return None

    @classmethod
    def get_all_records(cls):
        """Get all records."""
        return [cls(obj) for obj in datastore.all(cls.record_type)]

    @classmethod
    def count(cls):
        """Return number of all records based on record type."""
        return len(list(datastore.all(cls.record_type)))

    def dumps(self, **kwargs):
        """Return pure Python dictionary with record metadata."""
        return deepcopy(dict(self))


class Server(Sip2RecordMetadata):
    """class for SIP2 server."""

    record_type = "server"

    @property
    def number_of_clients(self):
        """Shortcut for number of clients."""
        return len(self.get_clients())

    @property
    def is_running(self):
        """Check if server is running.

        Reflects the recorded status only. A server killed without the chance
        to deregister itself still reads as running, so pair this with
        :attr:`is_alive` before trusting it.
        """
        return self.get("status") == "running"

    @property
    def is_alive(self):
        """Check whether the process holding this registration still exists.

        A `running` status is only meaningful while the process that wrote it
        is around. Two things can make it a lie: the process was killed
        outright (SIGKILL, OOM, host reboot), or the whole container was
        replaced, in which case the recorded pid belongs to a namespace that
        no longer exists and any pid check here would be meaningless.

        The recorded hostname settles the second case. Registrations written
        before hostnames were recorded fall back to checking the pid locally,
        which is the best evidence left: it still protects a server that is
        genuinely running here, and it lets a registration stranded by the
        upgrade itself be reclaimed instead of blocking every restart.

        :returns: False when the registration is provably stale.
        :rtype: bool
        """
        process_id = self.get("process_id")
        if not process_id:
            # Nothing to check against, so nothing can be proven.
            return True
        hostname = self.get("hostname")
        if hostname and hostname != socket.gethostname():
            # Written by another machine, or by a previous container: the pid
            # cannot be checked from here, but the writer is certainly gone.
            return False
        try:
            process = psutil.Process(process_id)
            started_at = self.get("started_at")
            if not started_at:
                return True
            # Guards against a pid recycled after a reboot: the process that
            # registered this server cannot have started after the
            # registration it is supposed to own.
            registered = datetime.fromisoformat(started_at).timestamp()
            created_at = process.create_time()
        except psutil.NoSuchProcess:
            return False
        except psutil.Error:
            # Cannot inspect it, so cannot prove it is stale.
            return True
        else:
            return created_at <= registered

    def delete(self):
        """Delete server and all attached clients."""
        self.clear_all_clients()
        super().delete()

    def get_clients(self):
        """Return clients."""
        filter_query = f"server:{self.id}"
        return self.search(index_type=Client.record_type, filter_query=filter_query)

    def down(self):
        """Set server status to `Down` and clear all clients data."""
        self["status"] = "down"
        self["stopped_at"] = datetime.now(UTC).isoformat()
        with contextlib.suppress(KeyError):
            del self["process_id"]
        self.update(self)
        # clear all clients
        self.clear_all_clients()

    def up(self):
        """Set server status to `running` and clear all clients data."""
        self["status"] = "running"
        self["started_at"] = datetime.now(UTC).isoformat()
        with contextlib.suppress(KeyError):
            del self["stopped_at"]
        self.update(self)

    def clear_all_clients(self):
        """Clear all clients."""
        for client in self.get_clients():
            Client(client).delete()

    @classmethod
    def create(cls, data, id_=None, force=False, **kwargs):
        """Create record.

        Reuses the existing registration when the server is already known.
        A registration still marked `running` whose owning process is gone is
        reclaimed rather than treated as a conflict, so that a server killed
        without a clean shutdown can be restarted without manual intervention.

        :param data: Dict with metadata.
        :param id_: Specify a UUID to use for the new record.
        :param force: Reclaim the registration even from a live server.
        :returns: The server record to run with.
        :rtype: Server
        :raises ServerAlreadyRunning: When another live process holds it.
        """
        # check if server already exist in datastore
        server = cls.find_server(**data)
        if server:
            # check if server running
            if server.is_running:
                if not force and server.is_alive:
                    msg = f"server already running {server.id}"
                    raise ServerAlreadyRunning(msg)
                logger.warning(
                    "reclaiming the registration of server %s held by pid %s on %s: %s",
                    server.get("server_name"),
                    server.get("process_id"),
                    server.get("hostname"),
                    "forced" if force else "that process is gone",
                )
                # Drops the stale status and the clients that went with it.
                server.down()
            # Hand the registration over to the process starting now. Only the
            # owner changes: the rest of `data` is what matched the lookup, and
            # rewriting the id would orphan the record under its old key.
            server.update({key: data[key] for key in SERVER_OWNER_KEYS if key in data})
            return server

        return super().create(data, id_=id_, **kwargs)

    @classmethod
    def find_server(cls, **kwargs):
        """Find server depending kwargs."""
        for key in SERVER_OWNER_KEYS:
            kwargs.pop(key, None)
        for server in datastore.all(cls.record_type):
            if kwargs.items() <= server.items():
                # true only if `first` is a subset of `second`
                return cls(server)
        return None


class Client(Sip2RecordMetadata):
    """class for selfcheck client."""

    record_type = "client"

    def get_key(self):
        """Get generated key for Client object."""
        return f"{self.record_type}:{self.id}_server:{self.server_id}"

    @property
    def server_id(self):
        """Get server identifier."""
        return self.get("server").get("id")

    def get_server(self):
        """Get server object."""
        return Server.get_record_by_id(self.server_id)

    @property
    def remote_app(self):
        """Shortcut for remote app."""
        return self.get_server().get("remote_app")

    @property
    def is_authenticated(self):
        """Shortcut to check if the selfcheck client is authenticated."""
        return self.get("authenticated", False)

    @property
    def terminal(self):
        """Shortcut to terminal."""
        return self.get("terminal", self.get("ip_address"))

    @property
    def transaction_user_id(self):
        """Shortcut to user id."""
        return self.get("transaction_user_id")

    @property
    def institution_id(self):
        """Shortcut to institution id."""
        return self.get("institution_id")

    @property
    def library_name(self):
        """Shortcut to library name."""
        return self.get("library_name")

    @property
    def library_language(self):
        """Shortcut for library language."""
        return self.get("library_language")

    def get_current_patron_session(self):
        """Shortcut to patron session."""
        return self.get("patron_session", None)

    def clear_patron_session(self):
        """Shortcut to library name."""
        with contextlib.suppress(KeyError):
            del self["patron_session"]

    @property
    def last_response_message(self):
        """Shortcut to user id."""
        return self.get("last_response", {})

    @property
    def last_request_message(self):
        """Shortcut to user id."""
        return self.get("last_request", {})

    @property
    def last_sequence_number(self):
        """Shortcut to user id."""
        return self.last_request_message.get("sequence_number")
