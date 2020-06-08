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

from .server import SocketServer


@click.group()
def selfcheck():
    """Automated Circulation System server management commands."""


@selfcheck.command('start')
@click.option(
    '-h', '--host', 'host', default=None,
    help='Host address of the server.'
)
@click.option(
    '-p', '--port', 'port', type=click.INT, default=None,
    help='Port that the server listen.'
)
@click.option(
    '-r', '--remote-app', 'remote',
    help='remote ILS application name in your config'
)
@with_appcontext
def start_socket_server(host, port, remote):
    """Start sockets server."""
    try:
        server = SocketServer(port=port, host=host, remote=remote)
        server_thread = threading.Thread(target=server.run)
        server_thread.run()
    except Exception as e:
        raise e
