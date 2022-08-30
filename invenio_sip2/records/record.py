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

"""API for manipulating the client."""


import contextlib
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from invenio_sip2 import current_datastore as datastore
from invenio_sip2.errors import ServerAlreadyRunning


class Sip2RecordMetadata(dict):
    """Sip2RecordMetadata class."""

    record_type = None

    def __init__(self, data, **kwargs):
        """Initialize instance with dictionary data.

        :param data: Dict with record metadata.
        """
        super(Sip2RecordMetadata, self).__init__(data or {})

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        """Create record.

        :param data: Dict with metadata.
        :param id_: Specify a UUID to use for the new record.
        """
        assert cls.record_type
        # TODO: check if record already exist and raise exception
        id_ = id_ or str(uuid4())

        data['id'] = id_
        record = cls(data, **kwargs)
        record['created'] = datetime.now(timezone.utc).isoformat()
        datastore.add(record, id_=id_, **kwargs)

        return record

    @property
    def id(self):
        """Shortcut for id."""
        return self.get('id', None)

    def get_key(self):
        """Get generated key for Sip2RecordMetadata object."""
        return '{record_type}:{id}'.format(
            record_type=self.record_type,
            id=self.id
        )

    def update(self, data):
        """Update instance with dictionary data.

        :param data: Dict with metadata.
        """
        if self.id:
            super(Sip2RecordMetadata, self).update(data)
            data['updated'] = datetime.now(timezone.utc).isoformat()
            datastore.update(self)

    def delete(self):
        """Delete record by uuid."""
        datastore.delete(self)

    def search(self, query='*', index_type=None, filter_query=None):
        """Search record by query."""
        return datastore.search(
            query, index_type=index_type, filter_query=filter_query)

    @classmethod
    def get_record_by_id(cls, id_):
        """Get record by uuid."""
        data = datastore.get(id_, cls.record_type)
        if data:
            return cls(data)

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

    record_type = 'server'

    @property
    def number_of_clients(self):
        """Shortcut for number of clients."""
        return len(self.get_clients())

    @property
    def is_running(self):
        """Check if server is running."""
        return self.get('status') == 'running'

    def delete(self):
        """Delete server and all attached clients."""
        self.clear_all_clients()
        super().delete()

    def get_clients(self):
        """Return clients."""
        filter_query = 'server:{server_id}'.format(
            server_id=self.id
        )
        return self.search(
            index_type=Client.record_type,
            filter_query=filter_query
        )

    def down(self):
        """Set server status to `Down` and clear all clients data."""
        self['status'] = 'down'
        self['stopped_at'] = datetime.now(timezone.utc).isoformat()
        with contextlib.suppress(KeyError):
            del self['process_id']
        self.update(self)
        # clear all clients
        self.clear_all_clients()

    def up(self):
        """Set server status to `running` and clear all clients data."""
        self['status'] = 'running'
        self['started_at'] = datetime.now(timezone.utc).isoformat()
        with contextlib.suppress(KeyError):
            del self['stopped_at']
        self.update(self)

    def clear_all_clients(self):
        """Clear all clients."""
        for client in self.get_clients():
            Client(client).delete()

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        """Create record.

        :param data: Dict with metadata.
        :param id_: Specify a UUID to use for the new record.
        """
        # check if server already exist in datastore
        server = cls.find_server(**data)
        if server:
            # check if server running
            if server.is_running:
                raise ServerAlreadyRunning(
                    'server already running {id}'.format(id=server.id)
                )
            return server

        return super().create(data, id_=id_)

    @classmethod
    def find_server(cls, **kwargs):
        """Find server depending kwargs."""
        with contextlib.suppress(KeyError):
            del kwargs['process_id']
        for server in datastore.all(cls.record_type):
            if kwargs.items() <= server.items():
                # true only if `first` is a subset of `second`
                return cls(server)


class Client(Sip2RecordMetadata):
    """class for selfcheck client."""

    record_type = 'client'

    def get_key(self):
        """Get generated key for Client object."""
        return '{record_type}:{id}_server:{server_id}'.format(
            record_type=self.record_type,
            id=self.id,
            server_id=self.server_id
        )

    @property
    def server_id(self):
        """Get server identifier."""
        return self.get('server').get('id')

    def get_server(self):
        """Get server object."""
        return Server.get_record_by_id(self.server_id)

    @property
    def remote_app(self):
        """Shortcut for remote app."""
        return self.get_server().get('remote_app')

    @property
    def is_authenticated(self):
        """Shortcut to check if the selfcheck client is authenticated."""
        return self.get('authenticated', False)

    @property
    def terminal(self):
        """Shortcut to terminal."""
        return self.get('terminal', self.get('ip_address'))

    @property
    def transaction_user_id(self):
        """Shortcut to user id."""
        return self.get('transaction_user_id')

    @property
    def institution_id(self):
        """Shortcut to institution id."""
        return self.get('institution_id')

    @property
    def library_name(self):
        """Shortcut to library name."""
        return self.get('library_name')

    @property
    def library_language(self):
        """Shortcut for library language."""
        return self.get('library_language')

    def get_current_patron_session(self):
        """Shortcut to patron session."""
        return self.get('patron_session', None)

    def clear_patron_session(self):
        """Shortcut to library name."""
        with contextlib.suppress(KeyError):
            del (self['patron_session'])

    @property
    def last_response_message(self):
        """Shortcut to user id."""
        return self.get('last_response',  {})

    @property
    def last_request_message(self):
        """Shortcut to user id."""
        return self.get('last_request', {})

    @property
    def last_sequence_number(self):
        """Shortcut to user id."""
        return self.last_request_message.get('sequence_number')
