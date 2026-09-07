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

import os
import socket

import click
import psutil
from flask.cli import with_appcontext
from psutil import AccessDenied, NoSuchProcess, TimeoutExpired

from invenio_sip2.records import Server
from invenio_sip2.server import SocketServer


@click.group()
def selfcheck():
    """Automated Circulation System server management commands."""


# TODO: create CLI to manage database


@selfcheck.command("start")
@click.argument("name")
@click.option(
    "-h", "--host", "host", default="0.0.0.0", help="Host address of the server."
)
@click.option(
    "-p",
    "--port",
    "port",
    type=click.INT,
    default=3004,
    help="Port that the server listen.",
)
@click.option(
    "-r",
    "--remote-app",
    "remote",
    help="remote ILS application name in your config",
    required=True,
)
@click.option(
    "-f",
    "--force",
    "force",
    is_flag=True,
    default=False,
    help="Take over the registration even from a server that is still alive.",
)
@with_appcontext
def start_socket_server(name, host, port, remote, force):
    """Start sockets server with unique name."""
    server = SocketServer(
        name=name,
        port=port,
        host=host,
        remote=remote,
        process_id=os.getpid(),
        force=force,
    )
    # Runs in this thread on purpose: signal handlers are only delivered to
    # the main thread, and the server installs its own to shut down cleanly.
    server.run()


@selfcheck.command("stop")
@click.argument("name")
@click.option("-d", "--delete", "delete", is_flag=True, default=False)
@click.option(
    "-t",
    "--timeout",
    "timeout",
    type=click.INT,
    default=30,
    help="Seconds to wait for the server to deregister itself.",
)
@with_appcontext
def stop_server(name, delete, timeout):
    """Stop sip2 server by unique name.

    Signals the process holding the registration and waits for it to
    deregister itself. This command only works on the same server or
    container.
    """
    server = Server.find_server(server_name=name)
    if not server:
        click.secho(f"no server named '{name}' is registered", fg="yellow")
        return

    if not server.is_running:
        click.echo("server already stopped")
    elif (hostname := server.get("hostname")) and hostname != socket.gethostname():
        click.secho(
            f"'{name}' is registered on a different host ({hostname}); this "
            "process cannot signal it from here. Run the stop command inside "
            "the container or host that owns the SIP2 server.",
            fg="yellow",
        )
    elif not (process_id := server.get("process_id")):
        # Nothing identifies the owner, and `psutil.Process(None)` is this very
        # process: signalling it would make the command kill itself.
        click.secho(
            f"'{name}' is registered as running but records no pid; marking it as down",
            fg="yellow",
        )
        server.down()
    elif not server.is_alive:
        # The registration outlived its process; there is nothing to signal
        # and the recorded pid must not be touched, it now belongs to
        # something else entirely.
        click.secho(
            f"'{name}' is registered as running by pid "
            f"{server.get('process_id')} on {server.get('hostname')}, which is "
            "gone; marking it as down",
            fg="yellow",
        )
        server.down()
    else:
        _terminate(server, name, process_id, timeout)

    if delete:
        server.delete()
        click.echo(f"deleted the registration of '{name}'")


def _terminate(server, name, process_id, timeout):
    """Signal the process holding a server registration and wait for it."""
    try:
        process = psutil.Process(process_id)
        click.echo(f"stop {name} (pid:{process_id})")
        process.terminate()
        process.wait(timeout=timeout)
    except NoSuchProcess:
        click.secho(f"pid {process_id} is already gone", fg="yellow")
    except TimeoutExpired:
        click.secho(
            f"'{name}' did not stop within {timeout}s; giving up on a clean "
            "shutdown and marking it as down",
            fg="red",
        )
    except AccessDenied:
        msg = (
            f"not allowed to signal pid {process_id}; run this as the user "
            "owning the SIP2 server process"
        )
        raise click.ClickException(msg) from None
    # The process deregisters itself on the way out, but say so unconditionally:
    # a killed or wedged process never gets that far, and leaving the
    # registration behind is exactly what forces a manual cleanup later.
    server.down()
