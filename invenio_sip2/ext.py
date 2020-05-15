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

"""Flask extension for Invenio-SIP2."""

from __future__ import absolute_import, print_function

from copy import deepcopy
from datetime import datetime, timezone

from flask import current_app
from werkzeug.utils import cached_property

from . import config
from .actions.actions import Action
from .errors import SelfCheckActionError
from .helpers import MessageTypeFixedField, MessageTypeVariableField
from .utils import convert_bool_to_char


class InvenioSIP2(object):
    """Invenio-SIP2 extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        app.extensions['invenio-sip2'] = self

    def init_config(self, app):
        """Initialize configuration."""
        # Use theme's base template if theme is installed

        app.config.setdefault(
            'SIP2_BASE_TEMPLATE',
            app.config.get('BASE_TEMPLATE', 'invenio_sip2/base.html')
        )

        for k in dir(config):
            if k.startswith('SIP2_'):
                app.config.setdefault(k, getattr(config, k))

        self.load_fixed_field(app)
        self.load_variable_field(app)

    def load_fixed_field(self, app):
        """Load fixed field configuration."""
        for name, field in app.config["SIP2_FIXED_FIELD_DEFINITION"].items():
            setattr(MessageTypeFixedField, name, MessageTypeFixedField(
                field_id=name,
                length=field.get('length'),
                label=field.get('label')
            ))

    def load_variable_field(self, app):
        """Load variable field configuration."""
        for name, field \
                in app.config["SIP2_VARIABLE_FIELD_DEFINITION"].items():
            setattr(MessageTypeVariableField, name, MessageTypeVariableField(
                field_id=field.get('field_id'),
                length=field.get('length', None),
                label=field.get('label')
            ))

    @cached_property
    def sip2(self):
        """Return the SIP2 action machine."""
        return _SIP2(
            action_config=deepcopy(
                current_app.config["SIP2_MESSAGE_ACTIONS"]
            )
        )

    @cached_property
    def sip2_message_types(self):
        """Message type configuration."""
        return _Sip2MessageType(
            message_type_config=deepcopy(
                current_app.config['SIP2_SELFCHECK_MESSAGE_TYPES']
            )
        )

    @property
    def sip2_current_date(self):
        """Get current date from system."""
        return datetime.now(timezone.utc).strftime(
            current_app.config['SIP2_DATE_FORMAT']
        )

    @cached_property
    def supported_protocol(self):
        """Supported protocol by the automated circulation system."""
        return current_app.config['SIP2_PROTOCOL']

    @cached_property
    def support_checkin(self):
        """Support of checkin by the automated circulation system."""
        return convert_bool_to_char(
            current_app.config['SIP2_SUPPORT_CHECKIN']
        )

    @cached_property
    def support_checkout(self):
        """Support of checkout by the automated circulation system."""
        return convert_bool_to_char(
            current_app.config['SIP2_SUPPORT_CHECKOUT']
        )

    @cached_property
    def support_online_status(self):
        """Support of online status by the automated circulation system."""
        return convert_bool_to_char(
            current_app.config['SIP2_SUPPORT_ONLINE_STATUS']
        )

    @cached_property
    def support_offline_status(self):
        """Support of offline status by the automated circulation system."""
        return convert_bool_to_char(
            current_app.config['SIP2_SUPPORT_OFFLINE_STATUS']
        )

    @cached_property
    def support_status_update(self):
        """Support of status update by the automated circulation system."""
        return convert_bool_to_char(
            current_app.config['SIP2_SUPPORT_STATUS_UPDATE']
        )

    @cached_property
    def support_renewal_policy(self):
        """Support of renewal policy by the automated circulation system."""
        return convert_bool_to_char(
            current_app.config['SIP2_SUPPORT_RENEWAL_POLICY']
        )

    @cached_property
    def timeout_period(self):
        """Timeout period allowed by the automated circulation system."""
        return current_app.config['SIP2_TIMEOUT_PERIOD']

    @cached_property
    def retries_allowed(self):
        """Number of retries allowed by the automated circulation system."""
        return current_app.config['SIP2_RETRIES_ALLOWED']

    @cached_property
    def supported_messages(self):
        """Supported messages by the automated circulation system."""
        # TODO: return supported message type from config
        return 'YYYYYYYYYYYYYYYY'


class _SIP2(object):
    """SIP2 action machine."""

    def __init__(self, action_config):
        """Constructor."""
        self.actions = {}
        for src_command, action in action_config.items():
            self.actions.setdefault(src_command, [])
            _cls = action.pop('action', Action)
            instance = _cls(**dict(action, command=src_command))
            self.actions[src_command] = instance

    def execute(self, msg, **kwargs):
        """Execute action on message."""
        try:
            action = self.actions[msg.command]
            return action.execute(msg, **kwargs)

        except SelfCheckActionError:
            pass


class _Sip2MessageType(object):

    message_types = {}

    def __init__(self, message_type_config):
        """Constructor."""
        for command, message_type in message_type_config.items():
            self.message_types[command] = _MessageType(command, **message_type)

    def get_by_command(self, command):
        return self.message_types.get(command, None)


class _MessageType(object):

    def __init__(self, command, **kwargs):
        self.command = command
        self.fixed_fields = []
        for fixed_field in kwargs.pop('fixed_fields', []):
            field = MessageTypeFixedField.get(fixed_field)
            self.fixed_fields.append(
                field
            )

        for key, value in kwargs.items():
            setattr(self, key, value)
