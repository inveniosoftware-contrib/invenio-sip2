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

from __future__ import absolute_import, print_function

import mock
import pytest

from invenio_sip2.actions.base import Action
from invenio_sip2.api import Message
from invenio_sip2.errors import CommandNotFound
from invenio_sip2.proxies import current_sip2


def test_sip2_actions_interface(app):
    """Test base action interface."""
    action = Action(command="93", response="94", message="interface_message")
    with pytest.raises(NotImplementedError):
        action.execute()

    with pytest.raises(CommandNotFound):
        action = Action(command="85", response="86", message="interface_message")
        action.execute()

    # test action from extension
    current_sip2.sip2.execute("wrong command")


@mock.patch(
    "invenio_sip2.actions.actions.selfcheck_login_handler",
    mock.MagicMock(return_value={"authenticated": False}),
)
def test_sip2_login_failed(app, dummy_client, failed_login_message):
    """Test login action failed."""

    response = current_sip2.sip2.execute(
        Message(request=failed_login_message), client=dummy_client
    )
    assert str(response) == "940AY0AZFDFE\r"


def test_sip2_login(app, dummy_client, login_message):
    """Test login action."""
    response = current_sip2.sip2.execute(
        Message(request=login_message), client=dummy_client
    )
    assert str(response) == "941AY1AZFDFC\r"


def test_sip2_system_status(app, dummy_client, system_status_message):
    """Test system status action."""
    response = current_sip2.sip2.execute(
        Message(request=system_status_message), client=dummy_client
    )
    assert str(response).startswith("98")


def test_patron_enable(app, dummy_client, enable_patron_message):
    """Test patron enable action."""
    response = current_sip2.sip2.execute(
        Message(request=enable_patron_message), client=dummy_client
    )
    assert str(response).startswith("26")


def test_patron_status(app, dummy_client, patron_status_message):
    """Test patron status action."""
    response = current_sip2.sip2.execute(
        Message(request=patron_status_message), client=dummy_client
    )
    assert str(response).startswith("24")


def test_patron_information(app, dummy_client, patron_information_message):
    """Test patron information action."""
    response = current_sip2.sip2.execute(
        Message(request=patron_information_message), client=dummy_client
    )
    data = response.dumps()
    required_fields = (
        app.config.get("SIP2_MESSAGE_TYPES").get("64").get("required_fields")
    )
    for field in required_fields:
        assert data[field]
    assert str(response).startswith("64")


def test_item_information(app, dummy_client, item_information_message):
    """Test patron enable action."""
    response = current_sip2.sip2.execute(
        Message(request=item_information_message), client=dummy_client
    )
    assert str(response).startswith("18")


def test_checkout(app, dummy_client, checkout_message):
    """Test checkout action."""
    response = current_sip2.sip2.execute(
        Message(request=checkout_message), client=dummy_client
    )
    assert str(response).startswith("12")


def test_checkin(app, dummy_client, checkin_message):
    """Test checkin action."""
    response = current_sip2.sip2.execute(
        Message(request=checkin_message), client=dummy_client
    )
    assert str(response).startswith("10")


def test_hold(app, dummy_client, create_hold_message):
    """Test hold action."""
    response = current_sip2.sip2.execute(
        Message(request=create_hold_message), client=dummy_client
    )
    assert str(response).startswith("16")


def test_renew(app, dummy_client, renew_message):
    """Test renew action."""
    response = current_sip2.sip2.execute(
        Message(request=renew_message), client=dummy_client
    )
    assert str(response).startswith("30")


def test_fee_paid(app, dummy_client, fee_paid_message):
    """Test checkin action."""
    response = current_sip2.sip2.execute(
        Message(request=fee_paid_message), client=dummy_client
    )
    assert str(response).startswith("38")


def test_end_patron_session(app, dummy_client, end_patron_session_message):
    """Test patron enable action."""
    # IMPORTANT NOTE:
    # this test needs to be run last, because during this test,
    # the patron session is deleted
    response = current_sip2.sip2.execute(
        Message(request=end_patron_session_message), client=dummy_client
    )
    assert str(response).startswith("36")
