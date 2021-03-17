# -*- coding: utf-8 -*-
#
# INVENIO-SIP2
# Copyright (C) 2021 UCLouvain
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

"""Module test."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_monitoring_status(app, users, server, dummy_client):
    """Test monitoring status."""
    with app.test_client() as client:
        res = client.get(url_for('api_sip2.status'))
        assert res.status_code == 401

        login_user_via_session(client, users.get('admin'))
        res = client.get(url_for('api_sip2.status'))
        assert res.status_code == 200


def test_monitoring_servers(app, users):
    """Test monitoring servers."""
    with app.test_client() as client:
        res = client.get(url_for('api_sip2.get_servers'))
        assert res.status_code == 401

        login_user_via_session(client, users.get('admin'))
        res = client.get(url_for('api_sip2.get_servers'))
        assert res.status_code == 200


def test_monitoring_clients(app, users):
    """Test monitoring servers."""
    with app.test_client() as client:
        res = client.get(url_for('api_sip2.get_clients'))
        assert res.status_code == 401

        login_user_via_session(client, users.get('admin'))
        res = client.get(url_for('api_sip2.get_clients'))
        assert res.status_code == 200


def test_get_server(app, users, server, dummy_client):
    """Test monitoring servers."""
    with app.test_client() as client:
        server_url = url_for(
            'api_sip2.get_server', server_id=server.id
        )
        res = client.get(server_url)
        assert res.status_code == 401

        login_user_via_session(client, users.get('admin'))
        res = client.get(server_url)
        assert res.status_code == 200
