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

"""SIP2 test helpers."""

import pytest

from invenio_sip2.errors import UnknownFieldIdMessageError
from invenio_sip2.helpers import MessageTypeFixedField, MessageTypeVariableField


def test_message_type_fixed_field():
    """Test message type fixed field."""
    field = MessageTypeFixedField.get("available")
    assert str(field)

    with pytest.raises(UnknownFieldIdMessageError):
        field = MessageTypeFixedField.get("dummy_field")


def test_message_type_variable_field():
    """Test message type fixed field."""
    field = MessageTypeVariableField.get("patron_id")
    assert str(field)

    with pytest.raises(UnknownFieldIdMessageError):
        field = MessageTypeVariableField.get("dummy_field")

    assert MessageTypeVariableField.find_by_field_id("AA")

    with pytest.raises(UnknownFieldIdMessageError):
        MessageTypeVariableField.find_by_field_id("dummy_field")
