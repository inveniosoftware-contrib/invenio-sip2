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

"""SIP2 helpers."""

from __future__ import absolute_import, print_function

from .errors import UnknownFieldIdMessageError


class MessageTypeFixedField(object):
    """SIP2 Message type fixed field helper class."""

    def __init__(self, field_id, length, label):
        """Constructor."""
        self.field_id = field_id
        self.length = length
        self.label = label

    def __str__(self):
        """String representation of fixed field."""
        return 'MessageTypeVariableField() field_id={field_id} ' \
               'length={length} label={label}' \
            .format(
                field_id=self.field_id,
                length=self.length,
                label=self.label)

    @classmethod
    def get(cls, name):
        """Get fixed field by name."""
        return getattr(cls, name)


class MessageTypeVariableField(object):
    """SIP2 Message type variable field helper class."""

    field_id_map = {}

    def __init__(self, field_id, label, length=None):
        """Constructor."""
        self.field_id = field_id
        self.label = label
        if length:
            self.length = length

        MessageTypeVariableField.field_id_map[field_id] = self

    def __str__(self):
        """String representation of variable field."""
        return 'MessageTypeVariableField() field_id={field_id} label={label}'\
            .format(
                field_id=self.field_id,
                label=self.label
            )

    @classmethod
    def get(cls, name):
        """Get variable field by name."""
        return getattr(cls, name)

    @classmethod
    def find_by_field_id(cls, field_id):
        """Find variable field by field id."""
        variable_field = cls.field_id_map.get(field_id)
        if variable_field is None:
            msg = "field id '{field_id}' not in [{field_id_map}]" \
                .format(field_id=field_id, field_id_map=cls.field_id_map)
            raise UnknownFieldIdMessageError(description=msg)
        return variable_field
