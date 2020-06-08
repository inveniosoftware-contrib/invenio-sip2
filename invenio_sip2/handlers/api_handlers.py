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

"""Handlers for customizing SIP2 APIs."""

from __future__ import absolute_import, print_function

from .base import base_authorize_patron_handler, base_enable_patron_handler, \
    base_patron_handlers, base_selfcheck_login_handler, \
    base_system_status_handler, base_validate_patron_handler


def selfcheck_login_handler(remote, login, password, **kwargs):
    """Handle selfcheck_ login functionality."""
    return base_selfcheck_login_handler(remote, login, password, **kwargs)


def system_status_handler(remote, message, **kwargs):
    """Handle  automatic circulation system status functionality."""
    return base_system_status_handler(remote, message, **kwargs)


def validate_patron_handler(remote, login, **kwargs):
    """Handle validate patron functionality."""
    return base_validate_patron_handler(remote, login, **kwargs)


def authorize_patron_handler(remote, login, password, **kwargs):
    """Handle authorize patron functionality."""
    return base_authorize_patron_handler(remote, login, password, **kwargs)


def enable_patron_handler(remote, patron_identifier, **kwargs):
    """Handle enable patron functionality."""
    return base_enable_patron_handler(remote, patron_identifier, **kwargs)


def patron_handlers(remote, patron_identifier, **kwargs):
    """Handle patron information functionality."""
    return base_patron_handlers(remote, patron_identifier, **kwargs)
