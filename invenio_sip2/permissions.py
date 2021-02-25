# -*- coding: utf-8 -*-
#
# INVENIO-SIP2
# Copyright (C) 2021 UCLouvain
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

"""Invenio-SIP2 permissions."""

from flask import abort
from flask_login import current_user
from invenio_access.permissions import Permission, SystemRoleNeed

admin_user = Permission(SystemRoleNeed('admin'))


def deny_all():
    """Deny all permission."""
    return type('Deny', (), {'can': lambda self: False})()


def check_permission(permission):
    """Abort if permission is not allowed.

    :param permission: The permission to check.
    """
    if permission is not None and not permission.can():
        if not current_user.is_authenticated:
            abort(401)
        abort(403)


def default_permission_factory(action):
    """Default api permission factory."""
    is_admin_user = ['api-monitoring']

    if action in is_admin_user:
        return admin_user

    return deny_all()
