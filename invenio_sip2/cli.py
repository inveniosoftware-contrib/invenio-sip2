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

"""CLI application for Invenio-SIP2."""


from __future__ import absolute_import, print_function

import threading

import click
from flask.cli import with_appcontext

from .errors import ServerAlreadyRunning
from .records.record import Server
from .server import SocketServer


@click.group()
def selfcheck():
    """Automated Circulation System server management commands."""


# TODO: create CLI to manage database

@selfcheck.command('start')
@click.argument('name')
@click.option(
    '-h', '--host', 'host', default='0.0.0.0',
    help='Host address of the server.'
)
@click.option(
    '-p', '--port', 'port', type=click.INT, default=3004,
    help='Port that the server listen.'
)
@click.option(
    '-r', '--remote-app', 'remote',
    help='remote ILS application name in your config',
    required=True
)
@with_appcontext
def start_socket_server(name, host, port, remote):
    """Start sockets server with unique name."""
    try:
        server = Server.find_server(server_name=name)
        if server and server.is_running:
            raise ServerAlreadyRunning(
                f'server [{name}] already running on {port}'
            )
        server = SocketServer(name=name, port=port, host=host, remote=remote)
        server_thread = threading.Thread(target=server.run)
        server_thread.run()

    except Exception as e:
        # TODO: log error
        raise e
