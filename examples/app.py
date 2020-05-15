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

"""Minimal Flask application example.

SPHINX-START

First install Invenio-SIP2, setup the application and load
fixture data by running:

.. code-block:: console

   $ pip install -e .[all]
   $ cd examples
   $ ./app-setup.sh
   $ ./app-fixtures.sh

Next, start the development server:

.. code-block:: console

   $ export FLASK_APP=app.py FLASK_DEBUG=1
   $ flask run

and open the example application in your browser:

.. code-block:: console

    $ open http://127.0.0.1:5000/

To reset the example application run:

.. code-block:: console

    $ ./app-teardown.sh

SPHINX-END
"""

from __future__ import absolute_import, print_function

import os

from flask import Flask
from flask_babelex import Babel
from invenio_db.ext import InvenioDB
from invenio_sip2 import InvenioSIP2
from invenio_sip2.views import blueprint

# Create Flask application
app = Flask(__name__)
app.config.update(
    SECRET_KEY="SECRET_KEY",
    # No permission checking
    RECORDS_REST_DEFAULT_READ_PERMISSION_FACTORY=None,
    SQLALCHEMY_TRACK_MODIFICATIONS=True,
    SQLALCHEMY_DATABASE_URI=os.getenv(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///app.db"
    ),
)
Babel(app)
InvenioDB(app)
InvenioSIP2(app)
app.register_blueprint(blueprint)
