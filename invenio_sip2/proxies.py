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

"""Helper proxy to the state object."""

import logging

from flask import current_app
from werkzeug.local import LocalProxy

current_sip2 = LocalProxy(
    lambda: current_app.extensions['invenio-sip2']
)

current_datastore = LocalProxy(
    lambda: current_app.extensions['invenio-sip2'].datastore
)

"""Helper proxy to get the current app sip2 extension."""
current_logger = LocalProxy(
    lambda: logging.getLogger('invenio-sip2')
)
"""Helper proxy to get the current logger."""
