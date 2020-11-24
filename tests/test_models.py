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

"""Test models."""

from __future__ import absolute_import, print_function

import pytest

from invenio_sip2.models import PatronStatus, PatronStatusTypes


def test_selfcheck_patron_status():
    """Test SIP2 patron status."""
    patron_status = PatronStatus()

    # test charged privileges denied status
    patron_status.add_patron_status_type(
        PatronStatusTypes.CHARGE_PRIVILEGES_DENIED
    )
    assert str(patron_status)[0] == 'Y'
    assert str(patron_status)[1] == ' '

    # test renewal privileges denied status
    patron_status = PatronStatus()
    patron_status.add_patron_status_type(
        PatronStatusTypes.RENEWAL_PRIVILEGES_DENIED
    )
    assert str(patron_status)[1] == 'Y'
    assert str(patron_status)[2] == ' '

    # test recall privileges denied status
    patron_status = PatronStatus()
    patron_status.add_patron_status_type(
        PatronStatusTypes.RECALL_PRIVILEGES_DENIED
    )
    assert str(patron_status)[2] == 'Y'
    assert str(patron_status)[3] == ' '

    # test hold privileges denied status
    patron_status = PatronStatus()
    patron_status.add_patron_status_type(
        PatronStatusTypes.HOLD_PRIVILEGES_DENIED
    )
    assert str(patron_status)[3] == 'Y'
    assert str(patron_status)[4] == ' '

    # test card lost status
    patron_status = PatronStatus()
    patron_status.add_patron_status_type(
        PatronStatusTypes.CARD_REPORTED_LOST
    )
    assert str(patron_status)[4] == 'Y'
    assert str(patron_status)[5] == ' '

    # test too many items charged status
    patron_status = PatronStatus()
    patron_status.add_patron_status_type(
        PatronStatusTypes.TOO_MANY_ITEMS_CHARGED
    )
    assert str(patron_status)[5] == 'Y'
    assert str(patron_status)[6] == ' '

    # test too many items overdue status
    patron_status = PatronStatus()
    patron_status.add_patron_status_type(
        PatronStatusTypes.TOO_MANY_ITEMS_OVERDUE
    )
    assert str(patron_status)[6] == 'Y'
    assert str(patron_status)[7] == ' '

    # test too many renewals status
    patron_status = PatronStatus()
    patron_status.add_patron_status_type(
        PatronStatusTypes.TOO_MANY_RENEWALS
    )
    assert str(patron_status)[7] == 'Y'
    assert str(patron_status)[8] == ' '

    # test too many claims status
    patron_status = PatronStatus()
    patron_status.add_patron_status_type(
        PatronStatusTypes.TOO_MANY_CLAIMS_OF_ITEMS_RETURNED
    )
    assert str(patron_status)[8] == 'Y'
    assert str(patron_status)[9] == ' '

    # test too many items lost status
    patron_status = PatronStatus()
    patron_status.add_patron_status_type(
        PatronStatusTypes.TOO_MANY_ITEMS_LOST
    )
    assert str(patron_status)[9] == 'Y'
    assert str(patron_status)[10] == ' '

    # test excessive outstanding fines status
    patron_status = PatronStatus()
    patron_status.add_patron_status_type(
        PatronStatusTypes.EXCESSIVE_OUTSTANDING_FINES
    )
    assert str(patron_status)[10] == 'Y'
    assert str(patron_status)[11] == ' '

    # test excessive outstanding fees status
    patron_status = PatronStatus()
    patron_status.add_patron_status_type(
        PatronStatusTypes.EXCESSIVE_OUTSTANDING_FEES
    )
    assert str(patron_status)[11] == 'Y'
    assert str(patron_status)[12] == ' '

    # test recall overdue status
    patron_status = PatronStatus()
    patron_status.add_patron_status_type(
        PatronStatusTypes.RECALL_OVERDUE
    )
    assert str(patron_status)[12] == 'Y'
    assert str(patron_status)[13] == ' '

    # test too many items billed status
    patron_status = PatronStatus()
    patron_status.add_patron_status_type(
        PatronStatusTypes.TOO_MANY_ITEMS_BILLED
    )
    assert str(patron_status)[13] == 'Y'

    # try to add unknown patron status type
    with pytest.raises(Exception):
        patron_status.add_patron_status_type(
            'unknown_patron_status_type'
        )
