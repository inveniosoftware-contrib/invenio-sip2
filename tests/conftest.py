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
import tempfile

import pytest
from flask import Flask
from flask_babelex import Babel
from invenio_access import ActionRoles, authenticated_user, superuser_access
from invenio_access.ext import InvenioAccess
from invenio_accounts.ext import InvenioAccounts
from invenio_accounts.models import Role
from invenio_accounts.testutils import create_test_user
from invenio_db import db
from invenio_db.ext import InvenioDB
from invenio_sip2 import InvenioSIP2
from invenio_sip2.server import SocketServer
from invenio_sip2.views import blueprint

pytest_plugins = [
    'fixtures.messages',
]


@pytest.fixture(scope='module')
def celery_config():
    """Override pytest-invenio fixture.

    TODO: Remove this fixture if you add Celery support.
    """
    return {}


@pytest.fixture(scope='module')
def app(request):
    """Flask application fixture."""
    instance_path = tempfile.mkdtemp()
    app = Flask(__name__, instance_path=instance_path)
    app.config.update(
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
        SERVER_NAME='localhost:5000',
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )
    Babel(app)
    InvenioSIP2(app)
    InvenioDB(app)
    InvenioAccess(app)
    InvenioAccounts(app)
    app.register_blueprint(blueprint)

    with app.app_context():
        db.create_all()
        yield app

    shutil.rmtree(instance_path)


@pytest.fixture(scope='module')
def create_app(instance_path):
    """Application factory fixture."""
    def factory(**config):
        app = Flask('testapp', instance_path=instance_path)
        app.config.update(
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
            SERVER_NAME='localhost:5000',
            TESTING=True,
            WTF_CSRF_ENABLED=False,
        )
        app.config.update(config or {})
        Babel(app)
        InvenioSIP2(app)
        InvenioDB(app)
        InvenioAccess(app)
        InvenioAccounts(app)
        app.register_blueprint(blueprint)
        return app
    return factory


@pytest.fixture(scope='module')
def dummy_socket_server(app):
    """Start server socket."""
    dummy_server = SocketServer(host='127.0.0.1', port=3005)
    yield dummy_server.run


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
