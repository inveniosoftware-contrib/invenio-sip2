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

from typing import ClassVar

from invenio_sip2.errors import UnknownFieldIdMessageError


class MessageTypeFixedField:
    """SIP2 Message type fixed field helper class."""

    def __init__(self, name, field):
        """Constructor."""
        self.field_id = name
        self.name = name
        self.label = field.get("label")
        self.length = field.get("length")
        self.callback = field.get("callback")
        self.fill = field.get("fill", " ")

    def __str__(self):
        """String representation of fixed field."""
        return (
            f"MessageTypeFixedField() field_id={self.field_id} "
            f"length={self.length} fill={self.fill} label={self.label}"
        )

    @classmethod
    def get(cls, name):
        """Get fixed field by name."""
        try:
            return getattr(cls, name)
        except AttributeError as e:
            raise UnknownFieldIdMessageError(message=name) from e


class MessageTypeVariableField:
    """SIP2 Message type variable field helper class."""

    field_id_map: ClassVar[dict] = {}

    def __init__(self, name, field):
        """Constructor."""
        self.field_id = field.get("field_id")
        self.name = name
        self.label = field.get("label")
        self.length = field.get("length")
        self.multiple = field.get("multiple", False)
        self.callback = field.get("callback")
        self.fill = field.get("fill", " ")

        MessageTypeVariableField.field_id_map[self.field_id] = self

    def __str__(self):
        """String representation of variable field."""
        return (
            f"MessageTypeVariableField() field_id={self.field_id} "
            f"length={self.length} fill={self.fill} label={self.label}"
        )

    @property
    def is_multiple(self):
        """Shorcut to check if variable field is multiple."""
        return self.multiple

    @classmethod
    def get(cls, name):
        """Get variable field by name."""
        try:
            return getattr(cls, name)
        except AttributeError as e:
            raise UnknownFieldIdMessageError from e

    @classmethod
    def find_by_field_id(cls, field_id):
        """Find variable field by field id."""
        variable_field = cls.field_id_map.get(field_id)
        if variable_field is None:
            msg = f"field id '{field_id}' not in [{cls.field_id_map}]"
            raise UnknownFieldIdMessageError(message=msg)
        return variable_field
