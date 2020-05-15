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

"""Invenio-SIP2 custom actions."""

from __future__ import absolute_import, print_function

from flask import current_app
from flask_security.utils import verify_password
from werkzeug.local import LocalProxy

from ..actions.base import Action, check_selfcheck_authentication
from ..proxies import current_sip2 as acs_system
from ..server import SocketServer

_datastore = LocalProxy(lambda: current_app.extensions['security'].datastore)


class SelfCheckLogin(Action):
    """Action to selfcheck login."""

    def execute(self, message, **kwargs):
        """Execute action."""
        selfcheck_login = message.get_field_value('login_uid')
        selfcheck_password = message.get_field_value('login_pwd')
        is_logged = '0'

        user_obj = _datastore.get_user(selfcheck_login)

        if user_obj and verify_password(selfcheck_password, user_obj.password):
            # TO DO: try to find other way to store authenticated status
            # for the current client maybe we can use redis cache to store
            # session ?
            client = kwargs.pop('client', None)
            if client:
                # TODO: store user id.
                SocketServer.clients[client[1]]['is_authenticated'] = True

            is_logged = '1'

        return str(self.prepare_message_response(
            ok=is_logged
        ))


class AutomatedCirculationSystemStatus(Action):
    """Action to get status from automated circulation system."""

    @check_selfcheck_authentication
    def execute(self, message, **kwargs):
        """Execute action."""
        # prepare message based on fixed fields
        response_message = self.prepare_message_response(
            online_status=acs_system.support_online_status,
            checkin_ok=acs_system.support_online_status,
            checkout_ok=acs_system.support_checkout,
            acs_renewal_policy=acs_system.support_renewal_policy,
            status_update_ok=acs_system.support_status_update,
            offline_ok=acs_system.support_offline_status,
            timeout_period=str(acs_system.timeout_period),
            retries_allowed=str(acs_system.retries_allowed),
            date_time_sync=acs_system.sip2_current_date,
            protocol_version=acs_system.supported_protocol
        )
        response_message.add_variable_field(
            field_name='supported_messages',
            field_value=acs_system.supported_messages
        )

        return str(response_message)
