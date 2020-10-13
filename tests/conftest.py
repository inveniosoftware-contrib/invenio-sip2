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

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

from __future__ import absolute_import, print_function

import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from subprocess import STDOUT

import pytest
from flask import Flask
from flask.cli import ScriptInfo
from flask_babelex import Babel
from invenio_access import ActionRoles, authenticated_user, superuser_access
from invenio_access.ext import InvenioAccess
from invenio_accounts.ext import InvenioAccounts
from invenio_accounts.models import Role
from invenio_accounts.testutils import create_test_user
from invenio_db.ext import InvenioDB
from utils import remote_authorize_patron_handler, remote_checkin_handler, \
    remote_checkout_handler, remote_enable_patron_handler, remote_handler, \
    remote_hold_handler, remote_item_information_handler, \
    remote_login_failed_handler, remote_login_handler, \
    remote_patron_account_handler, remote_renew_handler, \
    remote_system_status_handler, remote_validate_patron_handler

from invenio_sip2 import InvenioSIP2
from invenio_sip2.models import SelfcheckClient
from invenio_sip2.views import blueprint

sys.path.append(os.path.dirname(__file__))

pytest_plugins = [
    'fixtures.messages',
]


@pytest.fixture(scope='module')
def celery_config():
    """Override pytest-invenio fixture.

    TODO: Remove this fixture if you add Celery support.
    """
    return {}


@pytest.yield_fixture()
def app(request):
    """Flask application fixture."""
    instance_path = tempfile.mkdtemp()
    _app = Flask('testapp', instance_path=instance_path)

    _app.config.update(
        ACCOUNTS_USE_CELERY=False,
        CELERY_ALWAYS_EAGER=True,
        CELERY_CACHE_BACKEND="memory",
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        CELERY_RESULT_BACKEND="cache",
        LOGIN_DISABLED=False,
        MAIL_SUPPRESS_SEND=True,
        SECRET_KEY="CHANGE_ME",
        SECURITY_PASSWORD_SALT="CHANGE_ME_ALSO",
        SECURITY_CONFIRM_EMAIL_WITHIN="2 seconds",
        SECURITY_RESET_PASSWORD_WITHIN="2 seconds",
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SERVER_NAME='localhost:5000',
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SIP2_REMOTE_ACTION_HANDLERS=dict(
            test=dict(
                login_handler=remote_login_handler,
                logout_handler=remote_handler,
                system_status_handler=remote_system_status_handler,
                patron_handlers=dict(
                    validate_patron=remote_validate_patron_handler,
                    authorize_patron=remote_authorize_patron_handler,
                    enable_patron=remote_enable_patron_handler,
                    account=remote_patron_account_handler,
                ),
                item_handlers=dict(
                    item=remote_item_information_handler,
                ),
                circulation_handlers=dict(
                    checkout=remote_checkout_handler,
                    checkin=remote_checkin_handler,
                    hold=remote_hold_handler,
                    renew=remote_renew_handler,
                )
            ),
            test_invalid=dict(
                login_handler=remote_login_failed_handler,
            ),
        )
    )
    Babel(_app)
    InvenioDB(_app)
    InvenioAccess(_app)
    InvenioAccounts(_app)
    InvenioSIP2(_app)

    _app.register_blueprint(blueprint)

    with _app.app_context():
        yield _app

    # Teardown instance path.
    shutil.rmtree(instance_path)


@pytest.yield_fixture()
def dummy_socket_server(app):
    """Start server socket."""
    with app.app_context():
        # Start socket server
        cmd = 'invenio selfcheck start -h 127.0.0.1 -p 3006 -r test'
        dummy_server = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE, stderr=STDOUT, preexec_fn=os.setsid,
            shell=True)
        time.sleep(10)
        yield dummy_server

    # Stop server
    os.killpg(dummy_server.pid, signal.SIGTERM)


@pytest.yield_fixture()
def selfcheck_client():
    """Test socket server."""
    # This is fake test client to attempt a connect and disconnect
    fake_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fake_client.settimeout(10)
    fake_client.connect(('127.0.0.1', 3006))
    yield fake_client

    fake_client.close()


@pytest.fixture(scope='module')
def dummy_client():
    """Dummy client."""
    client1 = SelfcheckClient(('127.0.0.1', '65565'), 'test')
    return client1


@pytest.fixture(scope='module')
def dummy_invalid_client():
    """Dummy client."""
    client2 = SelfcheckClient(('127.0.0.1', '65565'), 'test_invalid')
    print('remote_app:', client2.remote_app)
    return client2


@pytest.fixture
def script_info(app):
    """Get ScriptInfo object for testing CLI."""
    return ScriptInfo(create_app=lambda info: app)


@pytest.fixture()
def users(db, app):
    """Create users."""
    # create users
    admin = create_test_user(
        email='admin@test.com',
        password='123456',
        active=True
    )
    librarian = create_test_user(
        email='librarian@test.com',
        password='123456',
        active=True
    )
    patron = create_test_user(
        email='patron@test.com',
        password='123456',
        active=True
    )

    with db.session.begin_nested():
        datastore = app.extensions['security'].datastore
        # Give role to admin
        admin_role = Role(name='admin')
        db.session.add(
            ActionRoles(action=superuser_access.value, role=admin_role)
        )
        datastore.add_role_to_user(admin, admin_role)
        # Give role to librarian
        librarian_role = Role(name='librarian')
        db.session.add(
            ActionRoles(action=authenticated_user.value, role=librarian_role)
        )
        datastore.add_role_to_user(librarian, librarian_role)
    db.session.commit()

    return {'admin': admin, 'librarian': librarian, 'user': patron}
