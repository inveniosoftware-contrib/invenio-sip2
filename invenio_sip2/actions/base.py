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

"""Invenio-SIP2 base actions."""

from __future__ import absolute_import, print_function

from functools import wraps

from ..api import Message
from ..proxies import current_sip2 as acs_system


def check_selfcheck_authentication(func):
    """Decorator to check authentication of selfcheck client."""

    @wraps(func)
    def inner(*args, **kwargs):
        client = kwargs.pop('client')
        if client and client.is_authenticated:
            return func(*args, client)

    return inner


class Action(object):
    """An action object used for automated circulation system."""

    def __init__(self, command, response, **kwargs):
        """Init action object."""
        self.command = command
        self.response_type = acs_system.sip2_message_types.get_by_command(
            response
        )
        self.validate_action()

    @property
    def required_fields(self):
        """Shortcut for optional fields."""
        return self.response_type.optional_fields

    @property
    def optional_fields(self):
        """Shortcut for optional fields."""
        return self.response_type.optional_fields

    def validate_action(self):
        """Ensure that type and action are valid."""
        # TODO: write logic to validate action
        return

    def prepare_message_response(self, **kwargs):
        """Prepare response message object based on defined fixed_field."""
        message = Message(
            message_type=self.response_type
        )
        for required_field in self.response_type.required_fields:
            field_value = kwargs.pop(required_field.name, None)
            message.add_field(
                field=required_field,
                field_value=field_value
            )
        for optional_field in self.response_type.optional_fields:
            field_value = kwargs.pop(optional_field.name, None)
            message.add_field(
                field=optional_field,
                field_value=field_value
            )
        # TODO: try to raise exception if fixed field does not exist
        return message

    def execute(self, **kwargs):
        """Execute before actions, action and after actions."""
        raise NotImplementedError()
