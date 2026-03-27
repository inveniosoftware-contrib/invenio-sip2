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

from invenio_sip2.permissions import check_permission


def check_selfcheck_authentication(func):
    """Decorator to check authentication of selfcheck client."""

    @wraps(func)
    def inner(*args, **kwargs):
        client = kwargs.pop("client")
        # TODO: maybe we can always call remote api to authenticate client
        if client and client.is_authenticated:
            return func(*args, client)
        return None

    return inner


def need_permission(actions):
    """Decorator to check authentication permission."""

    def decorator(func):
        @wraps(func)
        def decorate_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"status": "error: Unauthorized"}), 401
            check_permission(current_app.config["SIP2_PERMISSIONS_FACTORY"](actions))
            return func(*args, **kwargs)

        return decorate_view

    return decorator


def add_sequence_number(func):
    """Decorator to add sequence_number to response message."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        request_message = args[1]
        sequence_number = request_message.sequence_number
        if sequence_number:
            result.sequence_number = sequence_number
        return result

    return wrapper


def extract_and_add_language_parameter(func):
    """Decorator to extract and add language.

    Extracts the language from the client and injects it into the wrapped
    function as a `language` argument.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Try to retrieve the `client` argument:
        # 1. from keyword arguments
        # 2. or from positional arguments by looking for an object
        #    that has a method named `get_current_patron_session`
        client = kwargs.get("client") or next(
            (a for a in args if hasattr(a, "get_current_patron_session")), None
        )

        if client is None:
            raise ValueError("Client not found")

        # Try to get the language from the patron session first,
        # otherwise fall back to the client's `library_language`
        patron_session = client.get_current_patron_session()
        language = (patron_session or {}).get("language") or client.get(
            "library_language"
        )

        # Call the original function, injecting the language
        return func(*args, language=language, **kwargs)

    return wrapper
