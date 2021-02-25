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

"""SIP2 decorators."""

from functools import wraps

from flask import current_app, jsonify
from flask_login import current_user

from .permissions import check_permission


def need_permission(actions):
    """Decorator to check authentication permission."""

    def decorator(func):
        @wraps(func)
        def decorate_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'status': 'error: Unauthorized'}), 401
            check_permission(
                current_app.config["SIP2_PERMISSIONS_FACTORY"](actions)
            )
            return func(*args, **kwargs)
        return decorate_view

    return decorator
