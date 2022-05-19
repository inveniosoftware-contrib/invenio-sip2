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

import logging
from copy import deepcopy
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from flask import current_app
from invenio_base.utils import obj_or_import_string
from werkzeug.utils import cached_property

from invenio_sip2 import config, handlers
from invenio_sip2.actions.actions import Action
from invenio_sip2.errors import CommandNotFound
from invenio_sip2.helpers import MessageTypeFixedField, \
    MessageTypeVariableField
from invenio_sip2.models import SupportedMessages
from invenio_sip2.utils import convert_bool_to_char
from invenio_sip2.version import __version__

logger = logging.getLogger('invenio-sip2')


def load_fixed_field(app):
    """Load fixed field configuration."""
    for name, field in app.config["SIP2_FIXED_FIELD_DEFINITION"].items():
        setattr(MessageTypeFixedField, name, MessageTypeFixedField(
            name=name,
            field=field
        ))


def load_variable_field(app):
    """Load variable field configuration."""
    for name, field \
            in app.config["SIP2_VARIABLE_FIELD_DEFINITION"].items():
        setattr(MessageTypeVariableField, name, MessageTypeVariableField(
            name=name,
            field=field
        ))


class InvenioSIP2(object):
    """Invenio-SIP2 extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        self._state = None
        self.datastore = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        # TODO: refactoring app init
        self.init_config(app)
        self._state = _Sip2State(app)

        # Set SIP2 datastore
        datastore_class = obj_or_import_string(
            app.config['SIP2_DATASTORE_HANDLER']
        )
        self.datastore = datastore_class(app)
        # Initialize logging
        if app.config['SIP2_LOGGING_CONSOLE']:
            self.add_console_handler(app)

        if app.config['SIP2_LOGGING_FS_LOGFILE']:
            self.add_fs_handler(app)

        app.extensions['invenio-sip2'] = self
        self.app = app

    def add_console_handler(self, app):
        """Add console handler to logger."""
        handler = logging.StreamHandler()
        handler.setFormatter(self.get_logging_formatter())
        self._add_logger_handler(handler,
                                 app.config['SIP2_LOGGING_CONSOLE_LEVEL'])

    def add_fs_handler(self, app):
        """Add file handler to logger."""
        handler = RotatingFileHandler(
            app.config['SIP2_LOGGING_FS_LOGFILE'],
            backupCount=app.config['SIP2_LOGGING_FS_BACKUPCOUNT'],
            maxBytes=app.config['SIP2_LOGGING_FS_MAXBYTES'],
            delay=True,
        )
        handler.setFormatter(self.get_logging_formatter())
        self._add_logger_handler(handler, app.config['SIP2_LOGGING_FS_LEVEL'])

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

        load_fixed_field(app)
        load_variable_field(app)

    def _add_logger_handler(self, handler, level):
        """Add handler to logger."""
        for h in logger.handlers:
            if isinstance(h, handler.__class__):
                return
        logger.setLevel(level)
        logger.addHandler(handler)

    @classmethod
    def get_logging_formatter(cls):
        """Return logging formatter."""
        log_format = \
            '%(asctime)s - %(name)s ({version}) - %(levelname)s - %(message)s'\
            .format(version=__version__)
        return logging.Formatter(log_format)

    @cached_property
    def sip2(self):
        """Return the SIP2 action machine."""
        return _SIP2(
            action_config=deepcopy(
                current_app.config["SIP2_MESSAGE_ACTIONS"]
            )
        )

    # TODO: reorganize extension implementation
    @cached_property
    def sip2_handlers(self):
        """Return the SIP2 handler machine."""
        return self._state

    @cached_property
    def sip2_message_types(self):
        """Message type configuration."""
        return _Sip2MessageType(
            message_type_config=deepcopy(
                current_app.config['SIP2_MESSAGE_TYPES']
            )
        )

    @property
    def sip2_language(self):
        """Get default language from system."""
        return current_app.config['SIP2_DEFAULT_LANGUAGE']

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
    def line_terminator(self):
        """Line terminator used for message."""
        return current_app.config['SIP2_LINE_TERMINATOR']

    @cached_property
    def text_encoding(self):
        """Message text charset encoding."""
        return current_app.config['SIP2_TEXT_ENCODING']

    @cached_property
    def is_error_detection_enabled(self):
        """Check if error detection is enabled."""
        return current_app.config['SIP2_ERROR_DETECTION']

    def supported_messages(self, remote_app):
        """Supported messages by the automated circulation system."""
        return self._state.supported_messages[remote_app]


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
            logger.debug(f'[_SIP2] execute action: {action}')
            return action.execute(msg, **kwargs)
        except Exception:
            pass


class _Sip2MessageType(object):

    message_types = {}

    def __init__(self, message_type_config):
        """Constructor."""
        for command, message_type in message_type_config.items():
            self.message_types[command] = _MessageType(command, **message_type)

    def get_by_command(self, command):
        try:
            return self.message_types[command]
        except Exception:
            err_msg = f"Command '{command}' not found"
            raise CommandNotFound(message=err_msg)


class _MessageType(object):

    def __init__(self, command, **kwargs):
        self.command = command
        self.required_fields = []
        self.optional_fields = []
        self.fixed_fields = []
        self.variable_fields = []
        self.label = kwargs.pop('label'),

        required_fields = kwargs.pop('required_fields', [])
        fixed_fields = kwargs.pop('fixed_fields', [])
        variable_fields = kwargs.pop('variable_fields', [])

        for required_field in required_fields:
            if required_field in fixed_fields:
                field = MessageTypeFixedField.get(required_field)
                self.fixed_fields.append(field)
            else:
                field = MessageTypeVariableField.get(required_field)
            self.required_fields.append(field)

        for variable_field in variable_fields:
            field = MessageTypeVariableField.get(variable_field)
            self.variable_fields.append(field)
            if variable_field not in required_fields:
                self.optional_fields.append(field)

        for key, value in kwargs.items():
            setattr(self, key, value)


class _Sip2State(object):
    """SIP2 state storing registered action handlers."""

    def __init__(self, app):
        """Initialize state."""
        self.app = app
        self.login_handler = {}
        self.system_status_handler = {}
        self.patron_handlers = {}
        self.item_handlers = {}
        self.circulation_handlers = {}
        self.supported_messages = {}

        # register api handlers
        for remote, conf in app.config['SIP2_REMOTE_ACTION_HANDLERS'].items():
            supported_messages = SupportedMessages()
            # register login handler
            if conf.get('login_handler'):
                self.login_handler[remote] = handlers.make_api_handler(
                    conf.get('login_handler'),
                    with_data=True
                )
                supported_messages.add_supported_message('login')

            if conf.get('system_status_handler'):
                self.system_status_handler[remote] = handlers.make_api_handler(
                    conf.get('system_status_handler'),
                    with_data=True
                )
                supported_messages.add_supported_message('system_status')

            # register patron handlers
            patron_handlers = {}
            for k, v in conf.get('patron_handlers', dict()).items():
                patron_handlers[k] = \
                    handlers.make_api_handler(v, with_data=True)
                supported_messages.add_supported_message(k)

            if patron_handlers:
                self.patron_handlers[remote] = patron_handlers

            # register item handlers
            item_handlers = {}
            for k, v in conf.get('item_handlers', dict()).items():
                item_handlers[k] = \
                    handlers.make_api_handler(v, with_data=True)
                supported_messages.add_supported_message(k)

            if item_handlers:
                self.item_handlers[remote] = item_handlers

            # register circulation handlers
            circulation_handlers = {}
            for k, v in conf.get('circulation_handlers', dict()).items():
                circulation_handlers[k] = \
                    handlers.make_api_handler(v, with_data=True)
                supported_messages.add_supported_message(k)

            if circulation_handlers:
                self.circulation_handlers[remote] = circulation_handlers

            self.supported_messages[remote] = supported_messages
