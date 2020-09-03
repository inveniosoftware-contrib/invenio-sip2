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

"""Pytest utils."""

from invenio_sip2.models import SelfcheckCirculationStatus, SelfcheckFeeType, \
    SelfcheckItemInformation, SelfcheckMediaType, SelfcheckPatronInformation, \
    SelfcheckPatronStatus, SelfcheckSecurityMarkerType


def str_to_bytes(string):
    """Convert string to bytes."""
    return bytes(string, 'utf-8')


def remote_handler():
    """Dummy remote handler function."""
    return lambda *args, **kwargs: 'TEST'


def remote_login_failed_handler(login, password):
    """Dummy remote handler for invalid login."""
    return {'authenticated': False}


def remote_login_handler(login, password):
    """Dummy remote handler for login."""
    return {
        'authenticated': True,
        'institution_id': 'selfcheck_location',
        'library_name': 'Name of the library'
    }


def remote_system_status_handler(login):
    """Dummy remote handler for system status."""
    return {'institution_id': 'selfcheck_location'}


def remote_authorize_patron_handler(patron_identifier, patron_password):
    """Dummy remote handler for authorize patron."""
    return True


def remote_validate_patron_handler(patron_identifier):
    """Dummy remote handler for validate patron."""
    return True


def remote_enable_patron_handler(patron_identifier):
    """Dummy remote handler for system status."""
    return {
        'patron_status': SelfcheckPatronStatus(),
        'language': 'und',
        'institution_id': 'selfcheck_location',
        'patron_id': 'patron_id',
        'patron_name': 'formatted patron name'
    }


def remote_patron_account_handler(patron_identifier):
    """Dummy remote handler for system status."""
    patron_account_information = SelfcheckPatronInformation(
        patron_id='patron_id',
        patron_name='formatted_patron_name',
        patron_email='patron_email',
        patron_phone='patron_phone',
        patron_address='patron_address',
        institution_id='institution_id',
        language='und',
        currency_type='EUR'
    )
    return patron_account_information


def remote_item_information_handler(barcode, item_pid, **kwargs):
    """Dummy remote handler for system status."""
    item_information = SelfcheckItemInformation(
        item_id='item_id',
        title_id='title_id',
        circulation_status=SelfcheckCirculationStatus.OTHER,
        fee_type=SelfcheckFeeType.OTHER,
        security_marker=SelfcheckSecurityMarkerType.OTHER
    )
    item_information['media_type'] = SelfcheckMediaType.OTHER
    item_information['hold_queue_length'] = 0
    item_information['owner'] = 'owner'
    item_information['permanent_location'] = 'permanent_location'
    item_information['current_location'] = 'current_location'
    return item_information
