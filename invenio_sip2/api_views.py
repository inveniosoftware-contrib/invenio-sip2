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

"""Blueprint for Invenio-SIP2."""

from __future__ import absolute_import, print_function

from flask import Blueprint, jsonify
from .records.record import Client, Server

api_blueprint = Blueprint(
    'api_sip2',
    __name__,
    url_prefix='/monitoring/sip2'
)


@api_blueprint.route('/test')
def tests():
    return jsonify({'sip2_test': 'ok'})


@api_blueprint.route('/servers')
def get_servers():
    """Display all running SIP2 servers."""
    try:
        servers = Server.get_all_records()
        return jsonify({'servers': servers})
    except Exception as error:
        raise error
        return jsonify({'ERROR': str(error)})


@api_blueprint.route('/servers/<string:server_id>')
def get_server(server_id):
    """Display all running SIP2 servers."""
    try:
        server = Server.get_record_by_id(server_id)
        server['clients'] = Monitoring.get_list_of_clients_by_server(server_id)
        return jsonify({
            'id': server.id,
            'metadata': server,
        })
    except Exception as error:
        raise error
        return jsonify({'ERROR': str(error)})


@api_blueprint.route('/clients')
def get_clients():
    """Display all connected clients to server."""
    try:
        clients = Client.get_all_records()
    except Exception as error:
        raise error
        return jsonify({'ERROR': str(error)})
    return jsonify({'clients': clients})


class Monitoring:
    """Monitoring class."""

    @classmethod
    def get_count_servers(cls):
        servers = Server.get_all_records()
        return len(servers)

    @classmethod
    def get_number_of_clients(cls):
        clients = Client.get_all_records()
        return len(clients)

    @classmethod
    def get_number_of_client_by_server(cls, server_id):
        server = Server.get_record_by_id(server_id)
        return server.number_of_clients

    @classmethod
    def get_list_of_servers(cls):
        servers = Server.get_all_records()
        return servers

    @classmethod
    def get_list_of_clients_by_server(cls, server_id):
        server = Server.get_record_by_id(server_id)
        if server:
            return server.get_clients()
