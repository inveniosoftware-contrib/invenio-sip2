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
from ..server import SocketServer


def check_selfcheck_authentication(func):
    """Decorator to check authentication of selfcheck client."""
    @wraps(func)
    def decorated_action(*args, **kwargs):
        client = kwargs.pop('client', None)
        if client and SocketServer.clients[client[1]]['is_authenticated']:
            return func(*args, **kwargs)
    return decorated_action


class Action(object):
    """An action object used for automated circulation system."""

    def __init__(self, command, response, **kwargs):
        """Init action object."""
        self.command = command
        self.response_type = acs_system.sip2_message_types.get_by_command(
            response
        )
        self.validate_actions()

    def validate_actions(self):
        """Ensure that type and action are valid."""
        return

    def prepare_message_response(self, **kwargs):
        """Prepare response message object based on defined fixed_field."""
        message = Message(
            message_type=self.response_type
        )
        for fixed_field in self.response_type.fixed_fields:
            field_value = kwargs.pop(fixed_field.field_id, None)
            if field_value:
                message.add_fixed_field(
                    field=fixed_field,
                    field_value=field_value
                )
            # TO DO: try to raise exception if fixed field does not exist
        return message

    def execute(self, **kwargs):
        """Execute before actions, action and after actions."""
        raise NotImplementedError()
