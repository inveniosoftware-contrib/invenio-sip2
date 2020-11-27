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

from invenio_sip2.storage.datastore import SIP2SimpleDatastore


def test_simple_datastore(app):
    """Simple datastore tests"""

    datastore = SIP2SimpleDatastore(app)

    datastore.put('key1', 'value1')
    datastore.put('key2', 'value2')

    assert 'value1' == datastore.get('key1')
    assert not datastore.get('dummy_key')

    datastore.delete('key1')
    assert not datastore.get('key1')

    datastore.flush()
    assert not datastore.get('key2')
