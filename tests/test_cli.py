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

"""CLI test."""

from datetime import UTC, datetime
from unittest.mock import patch

from click.testing import CliRunner
from psutil import AccessDenied, TimeoutExpired

from invenio_sip2.cli import selfcheck, start_socket_server, stop_server
from invenio_sip2.datastore import Sip2RedisDatastore
from invenio_sip2.records.record import Server

from .test_datastore import DEAD_PID, registration


def test_basic_cli():
    """Test version import."""
    res = CliRunner().invoke(selfcheck, ["--help"])
    assert res.exit_code == 0


def test_start_server_socker(app):
    """Test start socket server."""
    runner = app.test_cli_runner()

    # test start server with wrong port
    result = runner.invoke(
        start_socket_server,
        ["test_server", "--host", "0.0.0.0", "--port", 78495, "--remote-app", "test"],
    )
    assert result.exit_code == 1


def test_stop_unknown_server(app):
    """Stopping something that was never registered says so."""
    with app.app_context():
        Sip2RedisDatastore(app).flush()
    result = app.test_cli_runner().invoke(stop_server, ["not_registered"])
    assert result.exit_code == 0
    assert "no server named 'not_registered' is registered" in result.output


def test_stop_stale_server(app):
    """A registration whose process is gone is marked down, not signalled."""
    with app.app_context():
        Sip2RedisDatastore(app).flush()
        server = Server.create(registration(server_name="stale", process_id=DEAD_PID))
        server.up()

    result = app.test_cli_runner().invoke(stop_server, ["stale"])
    assert result.exit_code == 0
    assert "marking it as down" in result.output
    with app.app_context():
        assert not Server.find_server(server_name="stale").is_running


def test_stop_server_without_pid_spares_the_current_process(app):
    """`psutil.Process(None)` is this process: it must never be signalled."""
    with app.app_context():
        Sip2RedisDatastore(app).flush()
        server = Server.create({"server_name": "no_pid"})
        server.up()
        assert server.is_running
        assert not server.get("process_id")

    result = app.test_cli_runner().invoke(stop_server, ["no_pid"])
    assert result.exit_code == 0
    assert "records no pid" in result.output
    # Reaching this line at all is the assertion that matters: the command
    # did not terminate the interpreter running the tests.
    with app.app_context():
        assert not Server.find_server(server_name="no_pid").is_running


def test_stop_server_on_another_host_requires_remote_shutdown(app):
    """A registration from a different container cannot be stopped here."""
    with app.app_context():
        Sip2RedisDatastore(app).flush()
        server = Server.create(
            registration(
                server_name="remote", hostname="another-container", process_id=DEAD_PID
            )
        )
        server.up()

    result = app.test_cli_runner().invoke(stop_server, ["remote"])
    assert result.exit_code == 0
    assert "different host" in result.output
    with app.app_context():
        server = Server.find_server(server_name="remote")
        assert server is not None
        assert server.is_running


def test_stop_marks_missing_pid_as_down(app):
    """A stale pid is treated as already gone, not as something to signal."""
    with app.app_context():
        Sip2RedisDatastore(app).flush()
        server = Server.create(
            registration(
                server_name="gone", process_id=DEAD_PID, hostname="cerisier.local"
            )
        )
        server.up()

    result = app.test_cli_runner().invoke(stop_server, ["gone"])

    assert result.exit_code == 0
    assert "which is gone; marking it as down" in result.output
    with app.app_context():
        assert not Server.find_server(server_name="gone").is_running


def test_stop_reports_timeout_and_marks_server_down(app):
    """A wedged SIP2 process is declared down after the grace period expires."""
    with app.app_context():
        Sip2RedisDatastore(app).flush()
        server = Server.create(registration(server_name="wedged", process_id=4242))
        server.up()

    class FakeProcess:
        def create_time(self):
            return datetime.now(UTC).timestamp() - 600

        def terminate(self):
            return None

        def wait(self, timeout):
            raise TimeoutExpired(pid=4242, name="sip2", seconds=timeout)

    with patch("invenio_sip2.cli.psutil.Process", return_value=FakeProcess()):
        result = app.test_cli_runner().invoke(stop_server, ["wedged", "--timeout", "1"])

    assert result.exit_code == 0
    assert "did not stop within 1s" in result.output
    with app.app_context():
        assert not Server.find_server(server_name="wedged").is_running


def test_stop_denies_access_to_foreign_process(app):
    """The CLI must fail clearly when the current user cannot signal the process."""
    with app.app_context():
        Sip2RedisDatastore(app).flush()
        server = Server.create(registration(server_name="denied", process_id=4242))
        server.up()

    class FakeProcess:
        def create_time(self):
            return datetime.now(UTC).timestamp() - 600

        def terminate(self):
            raise AccessDenied(pid=4242, name="sip2")

        def wait(self, timeout):
            return None

    with patch("invenio_sip2.cli.psutil.Process", return_value=FakeProcess()):
        result = app.test_cli_runner().invoke(stop_server, ["denied"])

    assert result.exit_code == 1
    assert "not allowed to signal pid 4242" in result.output


def test_stop_deletes_the_registration(app):
    """`--delete` removes the record so a rename or reconfigure can start clean."""
    with app.app_context():
        Sip2RedisDatastore(app).flush()
        Server.create(registration(server_name="doomed", process_id=DEAD_PID)).up()

    result = app.test_cli_runner().invoke(stop_server, ["doomed", "--delete"])
    assert result.exit_code == 0
    with app.app_context():
        assert Server.find_server(server_name="doomed") is None
