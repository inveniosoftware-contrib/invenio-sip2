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

"""Handlers for customizing sip2 api."""

from invenio_sip2.handlers.api_handlers import authorize_patron_handler, \
    checkin_handler, checkout_handler, enable_patron_handler, hold_handler, \
    item_handler, patron_handler, patron_status_handler, renew_handler, \
    selfcheck_login_handler, system_status_handler, validate_patron_handler
from invenio_sip2.handlers.utils import make_api_handler

__all__ = (
    'make_api_handler',
    'selfcheck_login_handler',
    'system_status_handler',
    'validate_patron_handler',
    'authorize_patron_handler',
    'enable_patron_handler',
    'patron_handler',
    'patron_status_handler',
    'item_handler',
    'checkout_handler',
    'checkin_handler',
    'hold_handler',
    'renew_handler',
)
