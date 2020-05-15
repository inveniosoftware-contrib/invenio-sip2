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

"""Socket server test."""

from __future__ import absolute_import, print_function

from invenio_sip2.api import Message
from invenio_sip2.proxies import current_sip2


def test_selfcheck_login_failed(users, selckeck_failed_login_message):
    """Test selfcheck login."""
    response = current_sip2.sip2.execute(
        Message(request=selckeck_failed_login_message),
        client=None
    )

    assert (response == '940')


def test_selfcheck_login_success(users,
                                 selckeck_login_message):
    """Test selfcheck login."""
    response = current_sip2.sip2.execute(
        Message(request=selckeck_login_message),
        client=None
    )
    assert(response == '941')
