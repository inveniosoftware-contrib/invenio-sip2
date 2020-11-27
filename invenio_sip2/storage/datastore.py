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


class Datastore:
    """Abstracted datastore."""

    def __init__(self, app=None, datastore=None):
        """Initialize the datastore."""

    def get(self, key):
        """Return the key value.

        :param key: the object's key
        """
        raise NotImplementedError

    def create(self, key, value):
        """Store the object.

        :param key: the object's key
        :param value: the stored object
        """
        raise NotImplementedError

    def update(self, key, value):
        """Store the object.

        :param key: the object's key
        :param value: the stored object
        """
        raise NotImplementedError

    def delete(self, key):
        """Delete the specific key."""
        raise NotImplementedError

    def flush(self):
        """Flush the datastore."""
        raise NotImplementedError

    def all(self):
        """Return all stored object in the datastore."""
        raise NotImplementedError

    def search(self, query):
        """Return all objects in the datastore corresponding to the query."""
        raise NotImplementedError
