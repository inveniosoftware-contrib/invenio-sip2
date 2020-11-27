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

from invenio_sip2.datastore import Sip2RedisDatastore
from invenio_sip2.records.record import Server


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
