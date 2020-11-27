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

"""CLI test."""

from __future__ import absolute_import, print_function

from click.testing import CliRunner

from invenio_sip2.cli import selfcheck, start_socket_server


def test_basic_cli():
    """Test version import."""
    res = CliRunner().invoke(selfcheck)
    assert res.exit_code == 0


def test_start_server_socker(app):
    """Test start socket server."""
    runner = app.test_cli_runner()

    # test start server with wrong port
    result = runner.invoke(start_socket_server, [
        'test_server', '--host', '0.0.0.0', '--port', 78495, '--remote-app',
        'test'])
    assert result.exit_code == 1
