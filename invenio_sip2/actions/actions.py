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

from invenio_sip2.api import Message

from ..actions.base import Action, check_selfcheck_authentication
from ..errors import SelfcheckCirculationError
from ..handlers import authorize_patron_handler, checkin_handler, \
    checkout_handler, enable_patron_handler, hold_handler, item_handler, \
    patron_handler, patron_status_handler, renew_handler, \
    selfcheck_login_handler, system_status_handler, validate_patron_handler
from ..models import SelfcheckSummary
from ..proxies import current_sip2 as acs_system
from ..utils import convert_bool_to_char, get_circulation_status, \
    get_language_code, get_security_marker_type


class SelfCheckLogin(Action):
    """Action to selfcheck login."""

    def execute(self, message, **kwargs):
        """Execute action."""
        selfcheck_login = message.get_field_value('login_uid')
        selfcheck_password = message.get_field_value('login_pwd')
        client = kwargs.pop('client')

        selfcheck_user = selfcheck_login_handler(
            client.remote_app, selfcheck_login, selfcheck_password,
            terminal_ip=client.get('ip_address')
        )

        if selfcheck_user:
            client.update(selfcheck_user)

        response_message = self.prepare_message_response(
            ok=str(int(client.is_authenticated))
        )
        return response_message


class AutomatedCirculationSystemStatus(Action):
    """Action to get status from automated circulation system."""

    @check_selfcheck_authentication
    def execute(self, message, client):
        """Execute action."""
        # TODO : calculate system status from remote app
        status = system_status_handler(client.remote_app,
                                       client.terminal,
                                       institution_id=client.institution_id)
        client['status'] = status
        # prepare message based on required fields
        response_message = self.prepare_message_response(
            online_status=acs_system.support_online_status,
            checkin_ok=acs_system.support_checkin,
            checkout_ok=acs_system.support_checkout,
            acs_renewal_policy=acs_system.support_renewal_policy,
            status_update_ok=acs_system.support_status_update,
            offline_ok=acs_system.support_offline_status,
            timeout_period=str(acs_system.timeout_period),
            retries_allowed=str(acs_system.retries_allowed),
            date_time_sync=acs_system.sip2_current_date,
            protocol_version=acs_system.supported_protocol,
            supported_messages=acs_system.supported_messages,
            institution_id=client.institution_id

        )
        # add variable field
        if client.library_name:
            response_message.add_variable_field(
                field_name='library_name',
                field_value=client.library_name
            )
        return response_message


class RequestResend(Action):
    """Action to resend last message."""

    def __init__(self, command):
        """Init action object."""
        self.command = command
        self.validate_action()

    @check_selfcheck_authentication
    def execute(self, message, client):
        """Execute action."""
        last_response_message = client.last_response_message
        return Message(
            request=last_response_message.get('_sip2')
        )


class PatronEnable(Action):
    """Action to enable patron on automated circulation system."""

    @check_selfcheck_authentication
    def execute(self, message, client):
        """Execute action."""
        patron_id = message.get_field_value('patron_id')

        is_valid_patron = validate_patron_handler(
            client.remote_app, patron_id, institution_id=client.institution_id
        )

        enabled_patron = enable_patron_handler(
            client.remote_app, patron_id, institution_id=client.institution_id
        )

        # prepare message based on required fields
        response_message = self.prepare_message_response(
            patron_status=str(enabled_patron.get('patron_status')),
            language=get_language_code(enabled_patron.get('language')),
            transaction_date=acs_system.sip2_current_date,
            institution_id=client.institution_id,
            patron_id=patron_id,
            patron_name=enabled_patron.get('patron_name'),
        )
        response_message.add_variable_field(
            field_name='valid_patron',
            field_value='Y' if is_valid_patron else 'N'
        )

        # check patron password
        patron_password = message.get_field_value('patron_pwd')
        if patron_password:
            is_authenticated = authorize_patron_handler(
                client.remote_app, patron_id, patron_password,
                institution_id=client.institution_id
            )

            response_message.add_variable_field(
                field_name='valid_patron_pwd',
                field_value='Y' if is_authenticated else 'N'
            )

        # add optional fields
        for optional_field in self.optional_fields:
            response_message.add_field(
                field=optional_field,
                field_value=enabled_patron.get(optional_field.name)
            )

        return response_message


class PatronStatus(Action):
    """Action to get patron status from automated circulation system."""

    @check_selfcheck_authentication
    def execute(self, message, client):
        """Execute action."""
        patron_id = message.get_field_value('patron_id')
        patron_status = patron_status_handler(
            client.remote_app, patron_id, institution_id=client.institution_id
        )

        response_message = self.prepare_message_response(
            patron_status=str(patron_status.get('patron_status')),
            language=message.language,
            transaction_date=acs_system.sip2_current_date,
        )

        # add optional fields
        for optional_field in self.optional_fields:
            response_message.add_field(
                field=optional_field,
                field_value=patron_status.get(optional_field.name)
            )

        return response_message


class PatronInformation(Action):
    """Action to get patron information from automated circulation system."""

    @check_selfcheck_authentication
    def execute(self, message, client):
        """Execute action."""
        patron_id = message.get_field_value('patron_id')
        patron_account = patron_handler(
            client.remote_app, patron_id, institution_id=client.institution_id
        )

        # TODO: better way to begin session
        # Begin session
        client['patron_session'] = {
            'patron_id': patron_id,
            'language': message.i18n_language
        }
        # prepare message based on required fields
        response_message = self.prepare_message_response(
            patron_status=str(patron_account.get('patron_status')),
            language=message.language,
            transaction_date=acs_system.sip2_current_date,
            hold_items_count=str(patron_account.hold_items_count),
            overdue_items_count=str(patron_account.overdue_items_count),
            charged_items_count=str(patron_account.charged_items_count),
            fine_items_count=str(patron_account.fine_items_count),
            recall_items_count=str(patron_account.recall_items_count),
            unavailable_holds_count=str(
                patron_account.unavailable_items_count),
            institution_id=client.institution_id,
            patron_id=patron_id,
            patron_name=patron_account.patron_name
        )

        summary = SelfcheckSummary(message.summary)

        # add optional fields
        for optional_field in self.optional_fields:
            # TODO: use custom handler to get specified summary field.
            if (optional_field.name in summary.fields and
                summary.is_needed(optional_field.name)) or \
                    optional_field.name not in summary.fields:
                response_message.add_field(
                    field=optional_field,
                    field_value=patron_account.get(optional_field.name)
                )

        # check patron password
        patron_password = message.get_field_value('patron_pwd')
        if patron_password:
            is_authenticated = authorize_patron_handler(
                client.remote_app, patron_account.patron_id, patron_password,
                institution_id=client.institution_id
            )
            response_message.add_variable_field(
                field_name='valid_patron_pwd',
                field_value='Y' if is_authenticated else 'N'
            )

        return response_message


class EndPatronSession(Action):
    """Action to end patron session on automated circulation system."""

    @check_selfcheck_authentication
    def execute(self, message, client):
        """Execute action."""
        client.clear_patron_session()

        # prepare message based on required fields
        response_message = self.prepare_message_response(
            end_session=True,
            transaction_date=acs_system.sip2_current_date,
            institution_id=client.institution_id,
            patron_id=message.get_field_value('patron_id')
        )

        # TODO: add optional fields

        return response_message


class ItemInformation(Action):
    """Action to get item information from automated circulation system."""

    @check_selfcheck_authentication
    def execute(self, message, client):
        """Execute action."""
        patron_session = client.get_current_patron_session()
        item_identifier = message.get_field_value('item_id')
        item_information = item_handler(
            client.remote_app, patron_session.get('patron_id'),
            item_identifier, terminal=client.terminal,
            language=patron_session.get('language'),
            institution_id=client.institution_id
        )

        # prepare message based on required fields
        response_message = self.prepare_message_response(
            circulation_status=get_circulation_status(
                item_information.get('circulation_status')),
            security_marker=get_security_marker_type(
                item_information.get('security_marker')),
            fee_type=item_information.get('fee_type'),
            transaction_date=acs_system.sip2_current_date,
            item_id=item_information.get('item_id'),
            title_id=item_information.get('title_id')
        )

        # add optional fields
        for optional_field in self.optional_fields:
            response_message.add_field(
                field=optional_field,
                field_value=item_information.get(optional_field.name)
            )

        return response_message


class BlockPatron(Action):
    """Action to block patron."""

    @check_selfcheck_authentication
    def execute(self, message, client, **kwargs):
        """Execute action."""
        # TODO: implements action
        return


class Checkin(Action):
    """Action to checkin an item."""

    @check_selfcheck_authentication
    def execute(self, message, client, **kwargs):
        """Execute checkin action."""
        patron_session = client.get_current_patron_session()
        item_id = message.get_field_value('item_id')

        try:
            # TODO: give the client to reduce the number of parameters.
            checkin = checkin_handler(
                client.remote_app, client.transaction_user_id, item_id,
                patron_id=patron_session.get('patron_id'),
                institution_id=client.institution_id,
                terminal=client.terminal,
                language=patron_session.get('language')
            )
        except SelfcheckCirculationError as error:
            checkin = error.data
            current_app.logger.error('[{terminal}] {message}'.format(
                terminal=client.terminal,
                message=error), exc_info=True)

        # prepare message based on required fields
        response_message = self.prepare_message_response(
            ok=str(int(checkin.is_success)),
            resensitize=checkin.resensitize,
            magnetic_media=checkin.has_magnetic_media,
            alert=convert_bool_to_char(checkin.sound_alert),
            transaction_date=acs_system.sip2_current_date,
            institution_id=client.institution_id,
            item_id=item_id,
            permanent_location=checkin.get('permanent_location'),
        )

        # add optional fields
        for optional_field in self.optional_fields:
            response_message.add_field(
                field=optional_field,
                field_value=checkin.get(optional_field.name)
            )

        return response_message


class Checkout(Action):
    """Action to checkout an item."""

    @check_selfcheck_authentication
    def execute(self, message, client, **kwargs):
        """Execute checkout action."""
        patron_session = client.get_current_patron_session()
        item_id = message.get_field_value('item_id')
        patron_id = message.get_field_value('patron_id')

        try:
            checkout = checkout_handler(
                client.remote_app, client.transaction_user_id, item_id,
                patron_id,
                institution_id=client.institution_id,
                terminal=client.terminal,
                language=patron_session.get('language')
            )
        except SelfcheckCirculationError as error:
            checkout = error.data
            current_app.logger.error('{message}'.format(
                message=error), exc_info=True)

        # prepare message based on required fields
        response_message = self.prepare_message_response(
            ok=str(int(checkout.is_success)),
            renewal_ok=checkout.is_renewal,
            magnetic_media=checkout.has_magnetic_media,
            desensitize=checkout.desensitize,
            transaction_date=acs_system.sip2_current_date,
            institution_id=client.institution_id,
            patron_id=patron_id,
            item_id=item_id,
            title_id=checkout.get('title_id'),
            due_date=checkout.due_date,
        )

        # add optional fields
        for optional_field in self.optional_fields:
            response_message.add_field(
                field=optional_field,
                field_value=checkout.get(optional_field.name)
            )

        return response_message


class FeePaid(Action):
    """Action to paid fee."""

    @check_selfcheck_authentication
    def execute(self, message, client, **kwargs):
        """Execute action."""
        # TODO: implements action
        return


class Hold(Action):
    """Action to hold an item."""

    @check_selfcheck_authentication
    def execute(self, message, client, **kwargs):
        """Execute hold action."""
        patron_session = client.get_current_patron_session()
        item_id = message.get_field_value('item_id')
        patron_id = message.get_field_value('patron_id')

        try:
            hold = hold_handler(
                client.remote_app, client.transaction_user_id, item_id,
                patron_id=patron_id,
                institution_id=client.institution_id,
                terminal=client.terminal,
                language=patron_session.get('language'),
            )
        except SelfcheckCirculationError as error:
            hold = error.data
            current_app.logger.error('[{terminal}] {message}'.format(
                terminal=client.terminal,
                message=error), exc_info=True)

        # prepare message based on required fields
        response_message = self.prepare_message_response(
            ok=str(int(hold.is_success)),
            available=hold.is_available,
            transaction_date=acs_system.sip2_current_date,
            institution_id=client.institution_id,
            patron_id=patron_id,
            item_id=item_id,
        )

        # add optional fields
        for optional_field in self.optional_fields:
            response_message.add_field(
                field=optional_field,
                field_value=hold.get(optional_field.name)
            )

        return response_message


class Renew(Action):
    """Action to renew an item."""

    @check_selfcheck_authentication
    def execute(self, message, client, **kwargs):
        """Execute checkout action."""
        patron_session = client.get_current_patron_session()
        item_id = message.get_field_value('item_id')
        patron_id = message.get_field_value('patron_id')

        try:
            renew = renew_handler(
                client.remote_app, client.transaction_user_id, item_id,
                patron_id=patron_id,
                intitution_id=client.institution_id,
                terminal=client.terminal,
                language=patron_session.get('language'),
            )
        except SelfcheckCirculationError as error:
            renew = error.data
            current_app.logger.error('[{terminal}] {message}'.format(
                terminal=client.terminal,
                message=error), exc_info=True)

        # prepare message based on required fields
        response_message = self.prepare_message_response(
            ok=str(int(renew.is_success)),
            renewal_ok=renew.is_renewal,
            magnetic_media=renew.has_magnetic_media,
            desensitize=renew.desensitize,
            transaction_date=acs_system.sip2_current_date,
            institution_id=client.institution_id,
            patron_id=patron_id,
            item_id=item_id,
            title_id=renew.get('title_id'),
            due_date=renew.get('due_date'),
        )

        # add optional fields
        for optional_field in self.optional_fields:
            response_message.add_field(
                field=optional_field,
                field_value=renew.get(optional_field.name)
            )

        return response_message


class RenewAll(Action):
    """Action to renew all items."""

    @check_selfcheck_authentication
    def execute(self, message, client, **kwargs):
        """Execute action."""
        # TODO: implements action
        return


class ItemStatusUpdate(Action):
    """Action to update item status."""

    @check_selfcheck_authentication
    def execute(self, message, client, **kwargs):
        """Execute action."""
        # TODO: implements action
        return
