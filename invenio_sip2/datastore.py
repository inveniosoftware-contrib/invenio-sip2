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

"""SIP2 socket server datastore."""

from abc import ABC, abstractmethod

import jsonpickle
from flask import current_app
from redis import StrictRedis


class Datastore(ABC):
    """Abstract datastore class."""

    @abstractmethod
    def get(self, id_):
        """Retrieve object for given id.

        :param id_: the object's id
        :return: the stored object
        """
        raise NotImplementedError

    @abstractmethod
    def add(self, key, value):
        """Store the object.

        :param key: the object's key
        :param value: the stored object
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, key, value):
        """Store the object.

        :param key: the object's key
        :param value: the stored object
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, key):
        """Delete the specific key."""
        raise NotImplementedError

    @abstractmethod
    def flush(self):
        """Flush the datastore."""
        raise NotImplementedError

    @abstractmethod
    def all(self):
        """Return all stored object in the datastore."""
        raise NotImplementedError

    @abstractmethod
    def search(self, query):
        """Return all objects in the datastore corresponding to the query."""
        raise NotImplementedError


class Sip2RedisDatastore(Datastore):
    """Redis datastore for sip2."""

    def __init__(self, app=None, **kwargs):
        """Initialize the datastore."""
        app = app or current_app
        redis_url = app.config['SIP2_DATASTORE_REDIS_URL']
        self.datastore = StrictRedis.from_url(redis_url)

    def get(self, id_, record_type=None):
        """Retrieve object for given id.

        :param id_: the object's id
        :param record_type: the object's type
        :return: the stored object
        """
        query = id_
        if record_type:
            query = '{record_type}:{id}*'.format(
                record_type=record_type,
                id=id_
            )
        for key in self._query(query):
            return jsonpickle.decode(self.datastore.get(key))

    def add(self, record, id_=None, **kwargs):
        """Store the object.

        :param record: the object
        :param id_: the object's id
        """
        self.datastore.set(record.get_key(), jsonpickle.encode(record.dumps()))

    def update(self, record, **kwargs):
        """Store the object.

        :param record: the object
        """
        self.datastore.set(record.get_key(), jsonpickle.encode(record.dumps()))

    def delete(self, record, record_type=None):
        """Delete the specific key.

        :param record: the object
        :param record_type: the object's type
        """
        self.datastore.delete(record.get_key())

    def flush(self):
        """Flush the datastore."""
        self.datastore.flushdb()

    def all(self, record_type=None):
        """Return all object in datastore.

        :param record_type: the object's type
        :return: list of stored objects
        """
        query = '*'
        if record_type:
            query = '{record_type}:*'.format(
                record_type=record_type
            )

        for key in self._query(query):
            yield jsonpickle.decode(self.datastore.get(key))

    def _query(self, query='*'):
        """Execute search query to datastore."""
        return self.datastore.keys(query)

    def search(self, search_term='*', index_type='*', filter_query=None):
        """Search object in th datastore."""
        search_key = '{record_type}:{search_term}'.format(
            record_type=index_type,
            search_term=search_term
        )
        if filter_query:
            search_key += '_{filter}'.format(
                filter=filter_query
            )

        return [jsonpickle.decode(self.datastore.get(key))
                for key in self._query(search_key)]
