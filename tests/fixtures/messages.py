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


@pytest.fixture(scope="module")
def selckeck_failed_login_message():
    """Selfcheck test login message."""
    return '9300CNinfo@test.org|COtester|CPselfcheck_location|AY0AZEB8C'


@pytest.fixture(scope="module")
def selckeck_login_message():
    """Selfcheck test login message."""
    return '9300CNlibrarian@test.com|CO123456|CPselfcheck_location|AY1AZEAEE'
