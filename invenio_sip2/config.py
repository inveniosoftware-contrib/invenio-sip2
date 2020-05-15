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

"""Invenio module that add SIP2 communication for self-check."""

from gettext import gettext as _

from .actions.actions import AutomatedCirculationSystemStatus, SelfCheckLogin
from .actions.base import Action

SIP2_TEXT_ENCODING = 'UTF-8'
SIP2_LINE_TERMINATOR = '\r'
SIP2_SOCKET_BUFFER_SIZE = '1024'
SIP2_CHECKSUM_CONTROL = True
SIP2_PROTOCOL = '2.00'

SIP2_SUPPORT_CHECKIN = True
SIP2_SUPPORT_CHECKOUT = True
SIP2_SUPPORT_RENEWAL_POLICY = True
SIP2_TIMEOUT_PERIOD = 10
SIP2_RETRIES_ALLOWED = 10
SIP2_SUPPORT_ONLINE_STATUS = True
SIP2_SUPPORT_OFFLINE_STATUS = True
SIP2_SUPPORT_STATUS_UPDATE = True
SIP2_DATE_FORMAT = '%Y%m%d    %H%M%S'

# Define message action.
SIP2_MESSAGE_ACTIONS = {
    '23': dict(response='24', action=Action),
    '11': dict(response='12', action=Action),
    '09': dict(response='10', action=Action),
    '01': dict(response='94', action=Action),
    '97': dict(response='96', action=Action),
    '63': dict(response='64', action=Action),
    '35': dict(response='36', action=Action),
    '37': dict(response='38', action=Action),
    '17': dict(response='18', action=Action),
    '19': dict(response='20', action=Action),
    '25': dict(response='26', action=Action),
    '15': dict(response='16', action=Action),
    '29': dict(response='30', action=Action),
    '65': dict(response='66', action=Action),
    '93': dict(response='94', action=SelfCheckLogin),
    '99': dict(response='98', action=AutomatedCirculationSystemStatus),
}

# Define message type
SIP2_SELFCHECK_MESSAGE_TYPES = {
    '01': dict(
        label='Block patron',
        handler='block_patron',
        fixed_fields=[
            'card_retained',
            'transaction_date',
        ],
    ),
    '09': dict(
        label='Checkin',
        handler='checkin',
        fixed_fields=[
            'no_block',
            'transaction_date',
            'return_date',
        ],
    ),
    '10': dict(
        label='Checkin response',
        handler='checkin_response',
        fixed_fields=[
            'ok',
            'resensitize',
            'magnetic_media',
            'alert',
            'transaction_date',
        ],
    ),
    '11': dict(
        label='Checkout',
        handler='checkout',
        fixed_fields=[
            'sc_renewal_policy',
            'no_block',
            'transaction_date',
            'nb_due_date',
        ],
    ),
    '12': dict(
        label='Checkout response',
        handler='checkout_response',
        fixed_fields=[
            'ok',
            'renewal_ok',
            'magnetic_media',
            'desensitize',
            'transaction_date',
        ],
    ),
    '15': dict(
        label='Hold',
        handler='hold',
        fixed_fields=[
            'hold_mode',
            'transaction_date',
        ],
    ),
    '16': dict(
        label='Hold response',
        handler='hold_response',
        fixed_fields=[
            'ok',
            'available',
            'transaction_date',
        ],
    ),
    '17': dict(
        label='Item information',
        handler='item_information',
        fixed_fields=[
            'transaction_date',
        ],
    ),
    '18': dict(
        label='Item information response',
        handler='item_information_response',
        fixed_fields=[
            'circulation_status',
            'security_marker',
            'fee_type',
            'transaction_date',
        ],
    ),
    '19': dict(
        label='Item status update',
        handler='item_status_update',
        fixed_fields=[
            'transaction_date',
        ],
    ),
    '20': dict(
        label='Item status update response',
        handler='item_status_update_response',
        fixed_fields=[
            'item_properties_ok',
            'transaction_date',
        ],
    ),
    '23': dict(
        label='Patron status',
        handler='patron_status',
        fixed_fields=[
            'language',
            'transaction_date',
        ],
    ),
    '24': dict(
        label='Patron status response',
        handler='patron_status_response',
        fixed_fields=[
            'patron_status',
            'language',
            'transaction_date',
        ],
    ),
    '25': dict(
        label='Patron enable',
        handler='patron_enable',
        fixed_fields=[
            'transaction_date',
        ],
    ),
    '26': dict(
        label='Patron enable response',
        handler='patron_enable_response',
        fixed_fields=[
            'patron_status',
            'language',
            'transaction_date',
        ],
    ),
    '29': dict(
        label='Renew',
        handler='renew',
        fixed_fields=[
            'third_party_allowed',
            'no_block',
            'nb_due_date',
            'transaction_date',
        ],
    ),
    '30': dict(
        label='Renew response',
        handler='renew_response',
        fixed_fields=[
            'ok',
            'renewal_ok',
            'magnetic_media',
            'desensitize',
            'transaction_date',
        ],
    ),
    '35': dict(
        label='End patron session',
        handler='end_patron_session',
        fixed_fields=[
            'transaction_date',
        ],
    ),
    '36': dict(
        label='End session response',
        handler='end_session_response',
        fixed_fields=[
            'end_session',
            'transaction_date',
        ],
    ),
    '37': dict(
        label='Fee paid',
        handler='fee_paid',
        fixed_fields=[
            'transaction_date',
            'fee_type',
            'payment_type',
            'currency_type',
        ],
    ),
    '38': dict(
        label='Fee paid response',
        handler='fee_paid_response',
        fixed_fields=[
            'transaction_date',
            'payment_accepted',
        ],
    ),
    '63': dict(
        label='Patron information',
        handler='patron_information',
        fixed_fields=[
            'language',
            'transaction_date',
            'summary',
        ],
    ),
    '64': dict(
        label='Patron information response',
        handler='patron_information',
        fixed_fields=[
            'patron_status',
            'language',
            'transaction_date',
            'hold_items_count',
            'overdue_items_count',
            'charged_items_count',
            'fine_items_count',
            'recall_items_count',
            'unavailable_holds_count',
        ],
    ),
    '65': dict(
        label='Renew all',
        handler='renew_all',
        fixed_fields=[
            'transaction_date',
        ],
    ),
    '66': dict(
        label='Renew all response',
        handler='renew_all_response',
        fixed_fields=[
            'ok',
            'renewed_count',
            'unrenewed_count',
            'transaction_date',
        ],
    ),
    '93': dict(
        label='Login',
        handler='login',
        fixed_fields=[
            'uid_algorithm',
            'pwd_algorithm',
        ],
    ),
    '94': dict(
        fixed_fields=[
            'ok'
        ]
    ),
    '96': dict(
        label='Request selfcheck resend',
        handler='request_sc_resend',
    ),
    '97': dict(
        label='Request Automated Circulation System resend',
        handler='request_acs_resend',
    ),
    '98': dict(
        label='Automated Circulation System status',
        handler='acs_status',
        fixed_fields=[
            'online_status',
            'checkin_ok',
            'checkout_ok',
            'acs_renewal_policy',
            'status_update_ok',
            'offline_ok',
            'timeout_period',
            'retries_allowed',
            'date_time_sync',
            'protocol_version',
        ],
    ),
    '99': dict(
        label='Selfcheck status',
        handler='selfcheck_status',
        fixed_fields=[
            'status_code',
            'max_print_width',
            'protocol_version',
        ],
    ),
}

SIP2_FIXED_FIELD_DEFINITION = dict(
    available=dict(length=1, label=_('transaction date')),
    transaction_date=dict(length=18, label=_('transaction date')),
    ok=dict(length=1, label=_('ok')),
    uid_algorithm=dict(length=1, label=_('uid algorithm')),
    pwd_algorithm=dict(length=1, label=_('pwd algorithm')),
    fee_type=dict(length=2, label=_('fee type')),
    payment_type=dict(length=2, label=_('payment type')),
    currency_type=dict(length=3, label=_('currency type')),
    payment_accepted=dict(length=1, label=_('payment accepted')),
    circulation_status=dict(length=2, label=_('circulation status')),
    security_marker=dict(length=2, label=_('security marker')),
    language=dict(length=3, label=_('language')),
    patron_status=dict(length=14, label=_('patron status')),
    end_session=dict(length=1, label=_('End Session')),
    summary=dict(length=10, label=_('summary')),
    hold_mode=dict(length=1, label=_('hold mode')),
    hold_items_count=dict(length=4, label=_('hold items count')),
    overdue_items_count=dict(length=4, label=_('overdue items count')),
    charged_items_count=dict(length=4, label=_('charged items count')),
    fine_items_count=dict(length=4, label=_('fine items count')),
    recall_items_count=dict(length=4, label=_('recall items count')),
    unavailable_holds_count=dict(length=4, label=_('unavailable holds count')),
    sc_renewal_policy=dict(length=1, label=_('sc renewal policy')),
    no_block=dict(length=1, label=_('no block')),
    card_retained=dict(length=1, label=_('card retained')),
    nb_due_date=dict(length=18, label=_('nb due date')),
    third_party_allowed=dict(length=1, label=_('Third party allowed')),
    renewal_ok=dict(length=1, label=_('renewal ok')),
    unrenewed_count=dict(length=4, label=_('renewal ok')),
    renewed_count=dict(length=4, label=_('renewal ok')),
    magnetic_media=dict(length=1, label=_('magnetic media')),
    desensitize=dict(length=1, label=_('desensitize')),
    resensitize=dict(length=1, label=_('resensitize')),
    return_date=dict(length=18, label=_('return date')),
    alert=dict(length=1, label=_('alert')),
    status_code=dict(length=1, label=_('status code')),
    max_print_width=dict(length=3, label=_('max print width')),
    protocol_version=dict(length=4, label=_('protocol version')),
    online_status=dict(length=1, label=_('on-line status')),
    checkin_ok=dict(length=1, label=_('checkin ok')),
    checkout_ok=dict(length=1, label=_('checkout ok')),
    item_properties_ok=dict(length=1, label=_('item properties ok')),
    acs_renewal_policy=dict(length=1, label=_('acs renewal policy')),
    status_update_ok=dict(length=1, label=_('status update ok')),
    offline_ok=dict(length=1, label=_('offline ok')),
    timeout_period=dict(length=3, label=_('timeout period')),
    retries_allowed=dict(length=3, label=_('retries allowed')),
    date_time_sync=dict(length=18, label=_('date/time sync')),
)

SIP2_VARIABLE_FIELD_DEFINITION = dict(
    patron_id=dict(field_id='AA', label=_('patron identifier')),
    item_id=dict(field_id='AB', label=_('item identifier')),
    terminal_pwd=dict(field_id='AC', label=_('terminal password')),
    patron_pwd=dict(field_id='AD', label=_('patron password')),
    patron_name=dict(field_id='AE', label=_('personal name')),
    screen_msg=dict(field_id='AF', label=_('screen message')),
    print_line=dict(field_id='AG', label=_('print line')),
    due_date=dict(field_id='AH', label=_('due date')),
    title_id=dict(field_id='AJ', label=_('title identifier')),
    blocked_card_msg=dict(field_id='AL', label=_('blocked card msg')),
    library_name=dict(field_id='AM', label=_('library name')),
    terminal_location=dict(field_id='AN', label=_('terminal location')),
    institution_id=dict(field_id='AO', label=_('institution id')),
    current_location=dict(field_id='AP', label=_('current location')),
    permanent_location=dict(field_id='AQ', label=_('permanent location')),
    hold_items=dict(field_id='AS', label=_('hold items')),
    overdue_items=dict(field_id='AT', label=_('overdue items')),
    charged_items=dict(field_id='AU', label=_('charged items')),
    fine_items=dict(field_id='AV', label=_('fine items')),
    sequence_number=dict(field_id='AY', length=1, label=_('sequence number')),
    checksum=dict(field_id='AZ', length=4, label=_('checksum')),
    home_address=dict(field_id='BD', label=_('home address')),
    email=dict(field_id='BE', label=_('e-mail address')),
    home_phone=dict(field_id='BF', label=_('home phone number')),
    owner=dict(field_id='BG', label=_('owner')),
    currency_type=dict(field_id='BH', length=3, label=_('currency type')),
    cancel=dict(field_id='BI', length=1, label=_('cancel')),
    transaction_id=dict(field_id='BK', label=_('transaction id')),
    valid_patron=dict(field_id='BL', length=1, label=_('valid patron')),
    renewed_items=dict(field_id='BM', label=_('renewed items')),
    unrenewed_items=dict(field_id='BN', label=_('unrenewed items')),
    fee_acknowledged=dict(field_id='BO', length=1, label=_('fee acknowledged')),
    start_item=dict(field_id='BP', label=_('start item')),
    end_item=dict(field_id='BQ', label=_('end item')),
    queue_position=dict(field_id='BR', label=_('queue position')),
    pickup_location=dict(field_id='BS', label=_('pickup location')),
    fee_type=dict(field_id='BT', length=2, label=_('fee type')),
    recall_items=dict(field_id='BU', label=_('recall items')),
    fee_amount=dict(field_id='BV', label=_('fee amount')),
    expiration_date=dict(field_id='BW', length=18, label=_('expiration date')),
    supported_messages=dict(field_id='BX', label=_('supported messages')),
    hold_type=dict(field_id='BY', length=1, label=_('hold type')),
    hold_items_limit=dict(field_id='BZ', length=4, label=_('hold items limit')),
    overdue_items_limit=dict(field_id='CA', length=4, label=_('overdue items limit')),
    charged_items_limit=dict(field_id='CB', length=4, label=_('charged items limit')),
    fee_limit=dict(field_id='CC', label=_('fee limit')),
    unavail_hold_items=dict(field_id='CD', label=_('unavailable hold items')),
    hold_queue_length=dict(field_id='CF', label=_('hold queue length')),
    fee_identifier=dict(field_id='CG', label=_('fee identifier')),
    item_properties=dict(field_id='CH', label=_('item properties')),
    security_inhibit=dict(field_id='CI', length=1, label=_('security inhibit')),
    recall_date=dict(field_id='CJ', length=18, label=_('recall date')),
    media_type=dict(field_id='CK', length=3, label=_('media type')),
    sort_bin=dict(field_id='CL', label=_('sort bin')),
    hold_pickup_date=dict(field_id='CM', length=18, label=_('hold pickup date')),
    login_uid=dict(field_id='CN', label=_('login user id')),
    login_pwd=dict(field_id='CO', label=_('login password')),
    location_code=dict(field_id='CP', label=_('location code')),
    valid_patron_pwd=dict(field_id='CQ', length=1, label=_('valid patron password')),
    patron_net_profile=dict(field_id='PI', label=_('patron internet profile')),
    call_number=dict(field_id='CS', label=_('call number')),
    collection_code=dict(field_id='CR', label=_('collection code')),
    alert_type=dict(field_id='CV', label=_('alert type')),
    hold_patron_id=dict(field_id='CY', label=_('hold patron id')),
    hold_patron_name=dict(field_id='DA', label=_('hold patron name')),
    destination_location=dict(field_id='CT', label=_('destination location')),
    patron_expire=dict(field_id='PA', label=_('patron expire date')),
    patron_birth_date=dict(field_id='PB', label=_('patron birth date')),
    patron_class=dict(field_id='PC', label=_('patron class')),
    register_login=dict(field_id='OR', label=_('register login')),
    check_number=dict(field_id='RN', label=_('check number')),
)
