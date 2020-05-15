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

"""Module test."""

from __future__ import absolute_import, print_function

from flask import Flask
from invenio_sip2 import InvenioSIP2


def test_version():
    """Test version import."""
    from invenio_sip2 import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = InvenioSIP2(app)
    assert 'invenio-sip2' in app.extensions

    app = Flask('testapp')
    ext = InvenioSIP2()
    assert 'invenio-sip2' not in app.extensions
    ext.init_app(app)
    assert 'invenio-sip2' in app.extensions


def test_view(app, base_client):
    """Test view."""
    res = base_client.get("/sip2/monitoring")
    assert res.status_code == 200
    assert 'Welcome to Invenio-SIP2' in str(res.data)
