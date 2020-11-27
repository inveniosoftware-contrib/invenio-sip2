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

from uuid import uuid4
# from invenio_record.dictutils import clear_none, dict_lookup
from invenio_sip2 import datastore
from copy import deepcopy


class Sip2RecordMetadata(dict):
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
        :param id_: Specify a UUID to use for the new record
        :param reindex: reindex metadata.
        """
        # TODO: check if record already exist and raise exception
        if not id_:
            id_ = str(uuid4())

        data['id'] = id_
        record = cls(data, **kwargs)
        datastore.create(record, id_=id_, **kwargs)

        return record

    @property
    def id(self):
        """Shortcut for id."""
        return self.get('id', None)

    def get_key(self):
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
        """get record by uuid."""
        data = datastore.get(id_, cls.record_type)
        if data:
            return cls(data)

    @classmethod
    def get_all_records(cls):
        """Get all records."""
        return [cls(obj) for obj in datastore.all(cls.record_type)]

    def dumps(self, **kwargs):
        """Return pure Python dictionary with record metadata."""
        return deepcopy(dict(self))


class Server(Sip2RecordMetadata):
    """class forSIP2 server."""

    record_type = 'server'

    @property
    def number_of_clients(self):
        """Get number of clients."""
        return len(self.get_clients())

    def get_clients(self):
        """Return clients."""
        filter_query = 'server:{server_id}'.format(
            server_id=self.id
        )
        return self.search(
            index_type=Client.record_type,
            filter_query=filter_query
        )


class Client(Sip2RecordMetadata):
    """class for selfcheck client."""

    record_type = 'client'

    def get_key(self):
        return '{record_type}:{id}_server:{server_id}'.format(
            record_type=self.record_type,
            id=self.id,
            server_id=self.server_id
        )

    @property
    def server_id(self):
        """Get socket server identifier."""
        return self.get('server').get('id')

    def get_server(self):
        """Get socket server identifier."""
        return Server.get_record_by_id(self.server_id)

    @property
    def remote_app(self):
        return self.get_server().get('remote_app')

    @property
    def is_authenticated(self):
        """Shortcut to check if the selfcheck client is authenticated."""
        return self.get('authenticated')

    @property
    def user_id(self):
        """Shortcut to user id."""
        return self.get('user_id')

    @property
    def institution_id(self):
        """Shortcut to institution id."""
        return self.get('institution_id')

    @property
    def library_name(self):
        """Shortcut to library name."""
        return self.get('library_name')

    def get_current_patron_session(self):
        """Shortcut to patron session."""
        return self.get('patron_session', None)

    def clear_patron_session(self):
        """Shortcut to library name."""
        del(self['patron_session'])
