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

"""Common pytest fixtures and plugins."""

import pytest
from utils import str_to_bytes


@pytest.fixture(scope="module")
def not_implemented_message():
    """Not implemented message."""
    return 'NOT_IMPLEMENTED_MESSAGE'


@pytest.fixture(scope="module")
def selfckeck_not_implemented_message(not_implemented_message):
    """Selfcheck Not implemented message."""
    return str_to_bytes(not_implemented_message)


@pytest.fixture(scope="module")
def failed_login_message():
    """Failed login message."""
    return '9300CNinfo@test.org|COtester|CPselfcheck_location|AY0AZEB8C'


@pytest.fixture(scope="module")
def selfckeck_failed_login_message(failed_login_message):
    """Selfcheck failed login message."""
    return str_to_bytes(failed_login_message)


@pytest.fixture(scope="module")
def login_message():
    """Login message."""
    return '9300CNlibrarian@test.com|CO123456|CPselfcheck_location|AY1AZEAEE'


@pytest.fixture(scope="module")
def selfckeck_login_message(login_message):
    """Selfcheck login message."""
    return str_to_bytes(login_message)


@pytest.fixture(scope="module")
def system_status_message():
    """Login message."""
    return '9900802.00AY1AZFCA0'


@pytest.fixture(scope="module")
def selfckeck_system_status_message(system_status_message):
    """Selfcheck system status message."""
    return str_to_bytes(system_status_message)


@pytest.fixture(scope="module")
def enable_patron_message():
    """Enable patron message."""
    return '2520200717    190253AOinstitution_id|AApatron_identifier|' \
           'AC|ADpatron_pwd'


@pytest.fixture(scope="module")
def patron_status_message():
    """Patron status message."""
    return '2300220201124    162421AOinstitution_id|AApatron_identifier|' \
           'ADpatron_pwd'


@pytest.fixture(scope="module")
def selfckeck_patron_status_message(system_status_message):
    """Selfcheck patron status message."""
    return str_to_bytes(patron_status_message)


@pytest.fixture(scope="module")
def selfckeck_validate_patron_message(enable_patron_message):
    """Selfcheck validate patron message."""
    return str_to_bytes(enable_patron_message)


@pytest.fixture(scope="module")
def patron_information_message():
    """Patron information message."""
    return '6300020200716    211818Y         AOinstitution_id' \
           '|AApatron_identifier|ADpatron_pwd|AY3AZECEC'


@pytest.fixture(scope="module")
def selfckeck_patron_information_message(patron_information_message):
    """Selfcheck patron message."""
    return str_to_bytes(patron_information_message)


@pytest.fixture(scope="module")
def end_patron_session_message():
    """End patron session message."""
    return '3520200717    192847AOinstitution_id|AApatron_identifier|' \
           'ADpatron_pwd'


@pytest.fixture(scope="module")
def selfckeck_end_patron_session_message(end_patron_session_message):
    """Selfcheck end patron session message."""
    return str_to_bytes(end_patron_session_message)


@pytest.fixture(scope="module")
def item_information_message():
    """Item information message."""
    return '1720201012    123755AOinstitution_id|ABitem_id|AY2AZF4D2'


@pytest.fixture(scope="module")
def selfckeck_item_information_message(item_information_message):
    """Selfcheck item message."""
    return str_to_bytes(item_information_message)


@pytest.fixture(scope="module")
def checkout_message():
    """Checkout message."""
    return '11YN20201013    09315820201013    093158AOinstitution_id|' \
           'AApatron_id|ABitem_id|ACterminal_password|AY0AZEC96'


@pytest.fixture(scope="module")
def selfckeck_checkout_message(checkout_message):
    """Selfcheck item message."""
    return str_to_bytes(checkout_message)


@pytest.fixture(scope="module")
def checkin_message():
    """Checkin message."""
    return '09N20201013    09315820201013    093158APinstitution_id|' \
           'AOinstitution_id|ABitem_id|ACterminal_password|AY0AZEC96'


@pytest.fixture(scope="module")
def selfckeck_checkin_message(checkin_message):
    """Selfcheck item message."""
    return str_to_bytes(checkout_message)


@pytest.fixture(scope="module")
def create_hold_message():
    """Create hold message."""
    return '15+20201013    093158|AOinstitution_id|AApatron_id|ABitem_id|' \
           'ACterminal_password|AY0AZEC96'


@pytest.fixture(scope="module")
def selfckeck_create_hold_message(create_hold_message):
    """Selfcheck create hold message."""
    return str_to_bytes(create_hold_message)


@pytest.fixture(scope="module")
def delete_hold_message():
    """Delete hold message."""
    return '15-20201013    093158|AOinstitution_id|AApatron_id|ABitem_id|' \
           'ACterminal_password|AY0AZEC96'


@pytest.fixture(scope="module")
def selfckeck_delete_hold_message(delete_hold_message):
    """Selfcheck delete hold message."""
    return str_to_bytes(delete_hold_message)


@pytest.fixture(scope="module")
def update_hold_message():
    """Update hold message."""
    return '15*20201013    093158|AOinstitution_id|AApatron_id|ABitem_id|' \
           'ACterminal_password|AY0AZEC96'


@pytest.fixture(scope="module")
def selfckeck_update_hold_message(update_hold_message):
    """Selfcheck create hold message."""
    return str_to_bytes(update_hold_message)


@pytest.fixture(scope="module")
def renew_message():
    """Renew message."""
    return '29NN20201013    09315820201013    09315|AOinstitution_id|' \
           'AApatron_id|ABitem_id|AY0AZEC96'


@pytest.fixture(scope="module")
def selfckeck_renew_message(renew_message):
    """Selfcheck create hold message."""
    return str_to_bytes(renew_message)


@pytest.fixture(scope="module")
def fee_paid_message():
    """Fee paid message."""
    return '3720221013    0931580402EUR|BV2.50|AOinstitution_id|AApatron_id' \
           '|CGfee_identifier|BKtransaction_id|AY0AZEC96'


@pytest.fixture(scope="module")
def selfckeck_fee_paid_message(fee_paid_message):
    """Selfcheck create fee paid message."""
    return str_to_bytes(fee_paid_message)
