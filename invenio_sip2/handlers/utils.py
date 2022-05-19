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

from functools import wraps

import six
from werkzeug.utils import import_string


def make_api_handler(func, with_data=True):
    """Make a handler for api callbacks.

    :param func: Callable or an import path to a callable
    :param with_data: Is data passed to function ?
    """
    if isinstance(func, six.string_types):
        func = import_string(func)

    @wraps(func)
    def inner(*args, **kwargs):
        if with_data:
            return func(args[0], *args[1:], **kwargs)
        else:
            return func(*args, **kwargs)
    return inner
