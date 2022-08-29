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

"""Invenio-sip2 actions test."""

import pytest

from invenio_sip2.api import Message
from invenio_sip2.errors import CommandNotFound, UnknownFieldIdMessageError


def test_messages_api(app, patron_information_message):
    """Test invenio-sip2 Message api."""
    # instantiate message class with wrong a message
    with pytest.raises(CommandNotFound):
        message = Message(request='bad sip2 message')

    # use well-formed message
    message = Message(request=patron_information_message)
    patron_id = message.get_field_values('patron_id')
    data = message.dumps()
    assert data['patron_id'] in patron_id
    for key in ['_sip2', 'message_type', 'institution_id', 'patron_id',
                'checksum', 'sequence_number', 'transaction_date']:
        assert data[key]
    # test unknown message field
    with pytest.raises(UnknownFieldIdMessageError):
        field = message.get_field_values('message_type')
