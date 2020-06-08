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
           'ADpatron_pwd'


@pytest.fixture(scope="module")
def selfckeck_validate_patron_message(enable_patron_message):
    """Selfcheck validate patron message."""
    return str_to_bytes(enable_patron_message)


@pytest.fixture(scope="module")
def patron_information_message():
    """Patron information message."""
    return '6300020200716    211818          AOinstitution_id' \
           '|AApatron_identifier|ADpatron_pwd|AY3AZECEC'


@pytest.fixture(scope="module")
def selfckeck_patron_information_message(patron_information_message):
    """Selfcheck validate patron message."""
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
