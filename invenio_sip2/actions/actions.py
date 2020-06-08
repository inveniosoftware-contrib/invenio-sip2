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

from ..actions.base import Action, check_selfcheck_authentication
from ..handlers import authorize_patron_handler, enable_patron_handler, \
    patron_handlers, selfcheck_login_handler, validate_patron_handler
from ..proxies import current_sip2 as acs_system
from ..utils import get_language_code


class SelfCheckLogin(Action):
    """Action to selfcheck login."""

    def execute(self, message, **kwargs):
        """Execute action."""
        selfcheck_login = message.get_field_value('login_uid')
        selfcheck_password = message.get_field_value('login_pwd')
        client = kwargs.pop('client')

        selfcheck_user = selfcheck_login_handler(
            client.remote_app, selfcheck_login, selfcheck_password
        )

        if selfcheck_user:
            # TODO: try to find other way to store authenticated client
            # maybe we can use redis cache to store session ?
            client.update(selfcheck_user)

        return str(self.prepare_message_response(
            ok='1' if client.is_authenticated else '0'
        ))


class AutomatedCirculationSystemStatus(Action):
    """Action to get status from automated circulation system."""

    @check_selfcheck_authentication
    def execute(self, message, client):
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
        # add variable field
        response_message.add_variable_field(
            field_name='supported_messages',
            field_value=acs_system.supported_messages
        )
        response_message.add_variable_field(
            field_name='institution_id',
            field_value=client.institution_id
        )
        if client.library_name:
            response_message.add_variable_field(
                field_name='library_name',
                field_value=client.library_name
            )
        return str(response_message)


class PatronEnable(Action):
    """Action to enable patron on automated circulation system."""

    @check_selfcheck_authentication
    def execute(self, message, client):
        """Execute action."""
        patron_identifier = message.get_field_value('patron_id')

        is_valid_patron = validate_patron_handler(
            client.remote_app, patron_identifier
        )

        enabled_patron = enable_patron_handler(
            client.remote_app, patron_identifier
        )

        # prepare message based on fixed fields
        response_message = self.prepare_message_response(
            patron_status=str(enabled_patron.get('patron_status')),
            language=get_language_code(enabled_patron.get('language')),
            transaction_date=acs_system.sip2_current_date,
        )
        response_message.add_variable_field(
            field_name='patron_id',
            field_value=patron_identifier
        )
        response_message.add_variable_field(
            field_name='institution_id',
            field_value=client.institution_id
        )

        response_message.add_variable_field(
            field_name='patron_name',
            field_value=enabled_patron.get('patron_name')
        )

        response_message.add_variable_field(
            field_name='valid_patron',
            field_value='Y' if is_valid_patron else 'N'
        )

        # check patron password
        patron_password = message.get_field_value('patron_pwd')
        if patron_password:
            is_authenticated = authorize_patron_handler(
                client.remote_app, patron_identifier, patron_password
            )

            response_message.add_variable_field(
                field_name='valid_patron_pwd',
                field_value='Y' if is_authenticated else 'N'
            )

        return str(response_message)


class PatronInformation(Action):
    """Action to get patron information from automated circulation system."""

    @check_selfcheck_authentication
    def execute(self, message, client):
        """Execute action."""
        # TODO: implements summary functionality
        patron_identifier = message.get_field_value('patron_id')

        is_valid_patron = validate_patron_handler(
            client.remote_app, patron_identifier
        )

        patron_account = patron_handlers(
            client.remote_app, patron_identifier
        )

        # prepare message based on fixed fields
        response_message = self.prepare_message_response(
            patron_status=str(patron_account.get('patron_status')),
            language=get_language_code(patron_account.get('language')),
            transaction_date=acs_system.sip2_current_date,
            hold_items_count=patron_account.hold_items_count,
            overdue_items_count=patron_account.overdue_items_count,
            charged_items_count=patron_account.charged_items_count,
            fine_items_count=patron_account.fine_items_count,
            recall_items_count=patron_account.recall_items_count,
            unavailable_holds_count=patron_account.unavailable_items_count,
        )

        # add variable field
        response_message.add_variable_field(
            field_name='institution_id',
            field_value=client.institution_id
        )
        response_message.add_variable_field(
            field_name='patron_id',
            field_value=patron_identifier
        )
        response_message.add_variable_field(
            field_name='patron_name',
            field_value=patron_account.get('patron_name')
        )
        response_message.add_variable_field(
            field_name='email',
            field_value=patron_account.get('patron_email')
        )

        response_message.add_variable_field(
            field_name='home_address',
            field_value=patron_account.get('patron_address')
        )

        response_message.add_variable_field(
            field_name='email',
            field_value=patron_account.get('patron_email')
        )

        response_message.add_variable_field(
            field_name='currency_type',
            field_value=patron_account.get('currency_type')
        )
        response_message.add_variable_field(
            field_name='fee_amount',
            field_value=patron_account.get('fee_amount')
        )

        response_message.add_variable_fields(
            field_name='hold_items',
            field_values=patron_account.get('hold_items', [])
        )

        response_message.add_variable_fields(
            field_name='overdue_items',
            field_values=patron_account.get('overdue_items', [])
        )

        response_message.add_variable_fields(
            field_name='charged_items',
            field_values=patron_account.get('charged_items', [])
        )

        response_message.add_variable_fields(
            field_name='fine_items',
            field_values=patron_account.get('fine_items', [])
        )

        response_message.add_variable_fields(
            field_name='recall_items',
            field_values=patron_account.get('recall_items', [])
        )

        response_message.add_variable_fields(
            field_name='unavailable_items',
            field_values=patron_account.get('unavailable_items', [])
        )

        response_message.add_variable_field(
            field_name='hold_items_limit',
            field_value=patron_account.get('hold_items_limit')
        )

        response_message.add_variable_field(
            field_name='overdue_items_limit',
            field_value=patron_account.get('overdue_items_limit')
        )

        response_message.add_variable_field(
            field_name='charged_items_limit',
            field_value=patron_account.get('charged_items_limit')
        )

        response_message.add_variable_field(
            field_name='valid_patron',
            field_value='Y' if is_valid_patron else 'N'
        )

        # check patron password
        patron_password = message.get_field_value('patron_pwd')
        if patron_password:
            is_authenticated = authorize_patron_handler(
                client.remote_app, patron_account.patron_id, patron_password
            )
            response_message.add_variable_field(
                field_name='valid_patron_pwd',
                field_value='Y' if is_authenticated else 'N'
            )

        return str(response_message)


class EndPatronSession(Action):
    """Action to end patron session on automated circulation system."""

    @check_selfcheck_authentication
    def execute(self, message, client):
        """Execute action."""
        # prepare message based on fixed fields
        response_message = self.prepare_message_response(
            end_session='Y',
            transaction_date=acs_system.sip2_current_date,
        )

        # add variable field
        response_message.add_variable_field(
            field_name='institution_id',
            field_value=client.institution_id
        )
        response_message.add_variable_field(
            field_name='patron_id',
            field_value=message.get_field_value('patron_id')
        )

        return str(response_message)
