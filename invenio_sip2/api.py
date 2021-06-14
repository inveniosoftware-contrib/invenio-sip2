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

"""Invenio-SIP2 API."""

from __future__ import absolute_import, print_function

from functools import wraps

from flask import current_app
from pycountry import languages

from .helpers import MessageTypeFixedField, MessageTypeVariableField
from .models import SelfcheckLanguage
from .proxies import current_sip2 as acs_system


def preprocess_field_value(func):
    """Decorator to preprocess field value."""

    @wraps(func)
    def inner(*args, **kwargs):
        field = kwargs.get('field')
        value = kwargs.get('field_value')
        if value and field.callback:
            return func(*args, field=field, field_value=field.callback(value))
        return func(*args, **kwargs)

    return inner


class FieldMessage(object):
    """SIP2 variable field message class."""

    def __init__(self, field=None, field_value=''):
        """Constructor."""
        self.field = field
        if field.length and len(field_value) < field.length:
            self.field_value = '{value:{fill}>{width}}'.format(
                value=str(field_value)[0:field.length],
                fill=self.field.fill,
                width=self.field.length
            )
        else:
            self.field_value = field_value

    def __str__(self):
        """String representation of FieldMessage object."""
        return self.field.field_id + (self.field_value or '') + '|'


class FixedFieldMessage(FieldMessage):
    """SIP2 fixed field message class."""

    def __str__(self):
        """String representation of FixedFieldMessage object."""
        return self.field_value


class Message(object):
    """SIP2 message."""

    def __init__(self, **kwargs):
        """Constructor."""
        self.variable_fields = []
        self.fixed_fields = []

        for key, value in kwargs.items():
            setattr(self, key, value)

        if hasattr(self, 'request'):
            self.message_text = self.request
            self.message_type = acs_system.sip2_message_types.get_by_command(
                self.message_text[:2]
            )
            self._parse_request()

    def __str__(self):
        """String representation of Message object."""
        if hasattr(self, 'message_text'):
            return self.message_text

        new_message = self.command

        for fixed_field in self.fixed_fields:
            new_message = new_message + str(fixed_field)

        for variable_field in self.variable_fields:
            new_message = new_message + str(variable_field)

        self.message_text = new_message
        return self.message_text

    @property
    def command(self):
        """Get command of the message type for SIP2 message."""
        return self.message_type.command

    @property
    def i18n_language(self):
        """Shortcut for i18n language."""
        try:
            language = SelfcheckLanguage(self.language).name
            return languages.get(name=language).alpha_2
        except (ValueError, AttributeError):
            # return default language
            return current_app.config.get('BABEL_DEFAULT_LANGUAGE')

    @property
    def language(self):
        """Shortcut for sip2 language code."""
        return self.get_fixed_field_value('language')

    @property
    def summary(self):
        """Shortcut for sip2 summary."""
        return self.get_fixed_field_value('summary')

    @property
    def sequence_number(self):
        """Get the sequence number."""
        return self.sequence

    def _parse_request(self):
        """Parse the request sended by the selfcheck."""
        if current_app.config.get('SIP2_ERROR_DETECTION'):
            # extract sequence number and checksum
            self.sequence = self.message_text[-7:-6]
            self.checksum = self.message_text[-4:]
            self.variable_fields.append(FieldMessage(
                MessageTypeVariableField.find_by_field_id('AY'),
                self.sequence))
            self.variable_fields.append(FieldMessage(
                MessageTypeVariableField.find_by_field_id('AZ'),
                self.checksum))

        # get remaining parts of the message
        txt = self.message_text[2:-9]

        # extract fixed fields from request
        for fixed_field in self.message_type.fixed_fields:
            # get fixed field value
            value = txt[:fixed_field.length]
            self.fixed_fields.append(FixedFieldMessage(fixed_field, value))
            txt = txt[fixed_field.length:]

        if not txt:
            return

        # extract variable fields from request
        for part in filter(None, txt.split('|')):
            field = MessageTypeVariableField.find_by_field_id(part[:2])
            if field is not None:
                self.variable_fields.append(FieldMessage(field, part[2:]))

    def get_fixed_field_by_name(self, field_name):
        """Get the FixedFieldMessage object by field name."""
        for f in self.fixed_fields:
            if f.field.field_id == MessageTypeFixedField.get(
                field_name
            ).field_id:
                return f

    def get_variable_field_by_name(self, field_name):
        """Get the VariableFieldMessage object by field name."""
        return next(self.get_variable_fields_by_name(field_name), None)

    def get_variable_fields_by_name(self, field_name):
        """Get list of VariableFieldMessage object by field name."""
        for f in self.variable_fields:
            if f.field.field_id == MessageTypeVariableField.get(
                field_name
            ).field_id:
                yield f

    def get_fixed_field_value(self, field_name):
        """Get fixed field value by field name."""
        fixed_field = self.get_fixed_field_by_name(field_name)
        if fixed_field:
            return fixed_field.field_value

    def get_field_value(self, field_name):
        """Get single variable field value by field name."""
        field = self.get_variable_field_by_name(field_name)
        if field:
            return field.field_value

    def get_field_values(self, field_name):
        """Get list of variable field value by field name."""
        fields = self.get_variable_fields_by_name(field_name)
        if fields:
            return [field.field_value for field in fields]

    @preprocess_field_value
    def add_field(self, field, field_value):
        """Add field to message according field type."""
        if field_value:
            if isinstance(field, MessageTypeFixedField):
                self.add_fixed_field(field, field_value)
            else:
                if field.is_multiple:
                    self.add_variable_fields(field.name, field_value)
                else:
                    self.add_variable_field(field.name, field_value)

    def add_variable_field(self, field_name, field_value):
        """Add variable field to message."""
        if field_value:
            self.variable_fields.append(
                FieldMessage(
                    field=MessageTypeVariableField.get(field_name),
                    field_value=str(field_value)
                )
            )

    def add_variable_fields(self, field_name, field_values):
        """Add variable fields to message."""
        for field_value in field_values:
            self.add_variable_field(field_name, field_value)

    def add_fixed_field(self, field, field_value):
        """Add fixed field to message."""
        self.fixed_fields.append(
            FixedFieldMessage(
                field=field,
                field_value=str(field_value)
            )
        )

    def dumps(self):
        """Dumps message as dict."""
        data = {}
        # TODO: `_sip2` field is only use in backend. Try to mask it on
        #       view or logging
        data['_sip2'] = str(self)
        data['message_type'] = {
            'command': self.message_type.command,
            'label': self.message_type.label
        }
        for fixed_field in self.fixed_fields:
            data[fixed_field.field.field_id] = fixed_field.field_value

        for variable_field in self.variable_fields:
            if variable_field.field.name not in ['login_uid',
                                                 'login_pwd',
                                                 'patron_pwd']:
                if variable_field.field.is_multiple:
                    field_list = data.get(variable_field.field.name, [])
                    field_list.append(variable_field.field_value)
                    data[variable_field.field.name] = field_list
                else:
                    data[variable_field.field.name] = \
                        variable_field.field_value
        return data
