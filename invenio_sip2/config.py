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

"""Configuration variables for defining invenio-sip2.

================================ ==============================================
`SIP2_DATASTORE_HANDLER`         datastore, default: `Sip2RedisDatastore`
`SIP2_DATASTORE_REDIS_PREFIX`    Prefix for redis keys, default `sip2`
`SIP2_DATASTORE_REDIS_URL`       Redis Datastore URL

`SIP2_MESSAGE_ACTIONS`           Dictionary of all selfcheck actions.
`SIP2_REMOTE_ACTION_HANDLERS`    Dictionary of remote action handlers.
                                 See example below.
`SIP2_MESSAGE_TYPES`             Define all message types conforming to SIP2
                                 protocol.
`SIP2_FIXED_FIELD_DEFINITION`    All fixed field available.
`SIP2_VARIABLE_FIELD_DEFINITION` All variable field available.
================================ ==============================================

Datastore handlers
^^^^^^^^^^^^^^^^^^

Use `SIP2_DATASTORE_HANDLER` to define your custom datastore.

Provided adaptor by invenio-sip2 is:
  :class: `invenio_sip2.datastore:Sip2RedisDatastore`

Remote action handlers
^^^^^^^^^^^^^^^^^^^^^^
Handlers allow customizing endpoints for each selfcheck actions.

Each custom handler actions must be defined in the ``SIP2_ACTIONS_HANDLERS``
dictionary, where the keys are the application names and the values the
configuration parameters for the application.

.. code-block:: python

    SIP2_REMOTE_ACTION_HANDLERS = dict(
        myapp=dict(
            # configuration values for myapp ...
        ),
    )

The application name is used to start invenio-sip2 server and call customized
handlers.

Configuration of a single remote application is a dictionary with the following
keys:

- ``login_handler`` - Import path to login selfcheck callback handler.
- ``logout_handler`` - Import path to logout selfcheck callback handler.
- ``system_status_handler`` - Import path to automated system status callback
    handler.
- ``patron_handlers`` - A dictionary of import path to patron callback handler.
    - ``validate_patron`` - Import path to validate patron callback handler.
    - ``authorize_patron`` - Import path to authorize patron  callback handler.
    - ``enable_patron`` - Import path to enable patron callback handler.
    - ``patron_status`` - Import path to patron status callback handler.
    - ``account`` - Import path to retrieve patron account callback handler.
- ``item_handlers`` - A dictionary of import path to item callback handler.
    - ``item`` - Import path to retrieve item callback handler.
- ``circulation_handlers`` - A dictionary of import path to circulation
    callback handler.
    - ``checkout`` - Import path to checkout item callback handler.
    - ``checkin`` - Import path to checkin item callback handler.
    - ``hold`` - Import path to hold item callback handler.
    - ``renew`` - Import path to renew item callback handler.
    - ``renew_all`` - Import path to renew_all items callback handler.

.. code-block:: python

    SIP2_REMOTE_ACTION_HANDLERS = dict(
        app=dict(
            login_handler="...",
            logout_handler="...",
            system_status_handler="...",
            patron_handlers=dict(
                validate_patron="...",
                authorize_patron="...",
                enable_patron="...",
                patron_status="...",
                account="...",
            ),
            item_handlers=dict(
                item="..."
            ),
            circulation_handlers=dict(
                checkout="...",
                checkin="...",
                hold="...",
                renew="...",
            )
        )
    )

"""

from gettext import gettext as _

from invenio_sip2.actions import AutomatedCirculationSystemStatus, \
    BlockPatron, Checkin, Checkout, EndPatronSession, FeePaid, Hold, \
    ItemInformation, ItemStatusUpdate, PatronEnable, PatronInformation, \
    PatronStatus, Renew, RenewAll, RequestResend, SelfCheckLogin
from invenio_sip2.models import SelfcheckSecurityMarkerType
from invenio_sip2.permissions import default_permission_factory
from invenio_sip2.utils import convert_bool_to_char, convert_to_char, \
    get_media_type, parse_circulation_date

# I18N
# ====
#: Default language
BABEL_DEFAULT_LANGUAGE = 'en'

#: Default SIP2 language
SIP2_DEFAULT_LANGUAGE = BABEL_DEFAULT_LANGUAGE

# DATASTORE
# =========
SIP2_DATASTORE_HANDLER = 'invenio_sip2.datastore:Sip2RedisDatastore'
SIP2_DATASTORE_REDIS_PREFIX = 'sip2'
SIP2_DATASTORE_REDIS_URL = 'redis://localhost:16379/0'

# LOGGING
# =======

# CONSOLE
SIP2_LOGGING_CONSOLE = True
"""Enable logging to the console."""

SIP2_LOGGING_CONSOLE_LEVEL = "INFO"
"""Console logging level.

All requests and responses will be written to the console if the level is on
info mode. Otherwise, they will not logged.
"""

# FILESYSTEM
SIP2_LOGGING_FS_LOGFILE = None
"""Enable logging to the filesystem.

A valid filesystem path is required to enable logging.
"""

SIP2_LOGGING_FS_LEVEL = "INFO"
"""Console logging level.

Defaults to write all requests and responses.
"""

SIP2_LOGGING_FS_BACKUPCOUNT = 5
"""Number of rotated log files to keep."""

SIP2_LOGGING_FS_MAXBYTES = 100 * 1024 * 1024
"""Maximum size of logging file. Default: 100MB."""

SIP2_PERMISSIONS_FACTORY = default_permission_factory
"""Define factory permissions."""

SIP2_REMOTE_ACTION_HANDLERS = {}
"""Configuration of remote handlers."""

SIP2_TEXT_ENCODING = 'UTF-8'
"""Message text charset encoding."""

SIP2_LINE_TERMINATOR = '\r'
"""Message line separator."""

SIP2_SOCKET_BUFFER_SIZE = '1024'
"""Socket buffer size."""

SIP2_ERROR_DETECTION = True
"""Enable error detection on message."""

SIP2_PROTOCOL = '2.00'
"""SIP2 protocol version."""

SIP2_SUPPORT_CHECKIN = True
"""Support check in items."""

SIP2_SUPPORT_CHECKOUT = True
"""Support check out items."""

SIP2_SUPPORT_RENEWAL_POLICY = True
"""Support patron renewal requests as a policy."""

SIP2_TIMEOUT_PERIOD = 10
"""Server timeout."""

SIP2_RETRIES_ALLOWED = 10
"""Number of retries allowed."""

SIP2_SUPPORT_ONLINE_STATUS = True
"""Support online status send by automatic circulation system."""

SIP2_SUPPORT_OFFLINE_STATUS = True
"""Support off line operation."""

SIP2_SUPPORT_STATUS_UPDATE = True
"""Support patron status updating by the selfcheck."""

SIP2_DATE_FORMAT = '%Y%m%d    %H%M%S'
"""SIP2 date format for transaction."""

SIP2_CIRCULATION_DATE_FORMAT = '%Y%m%d    %H%M%S'
"""SIP2 date format for circulation."""

SIP2_DEFAULT_SECURITY_MARKER = SelfcheckSecurityMarkerType.OTHER
"""SIP2 default security marker type."""

# Define message action.
SIP2_MESSAGE_ACTIONS = {
    '01': dict(message='block_patron', response='24', action=BlockPatron),
    '09': dict(message='checkin', response='10', action=Checkin),
    '11': dict(message='checkout', response='12', action=Checkout),
    '15': dict(message='hold', response='16', action=Hold),
    '17': dict(message='item_information', response='18',
               action=ItemInformation),
    '19': dict(message='item_status_update', response='20',
               action=ItemStatusUpdate),
    '23': dict(message='patron_request_status', response='24',
               action=PatronStatus),
    '25': dict(message='patron_enable', response='26', action=PatronEnable),
    '29': dict(message='renew', response='30', action=Renew),
    '35': dict(message='end_patron_session', response='36',
               action=EndPatronSession),
    '37': dict(message='fee_paid', response='38', action=FeePaid),
    '63': dict(message='patron_information', response='64',
               action=PatronInformation),
    '65': dict(message='renew_all', response='66', action=RenewAll),
    '93': dict(message='login', response='94', action=SelfCheckLogin),
    '97': dict(message='request_resend', action=RequestResend),
    '99': dict(message='sc_status', response='98',
               action=AutomatedCirculationSystemStatus),
}

# Define message types
SIP2_MESSAGE_TYPES = {
    '01': dict(
        label='Block patron',
        handler='block_patron',
        required_fields=[
            'card_retained',
            'transaction_date',
            'institution_id',
            'blocked_card_msg',
            'patron_id',
            'terminal_pwd',
        ],
        fixed_fields=[
            'card_retained',
            'transaction_date',
        ],
        variable_fields=[
            'institution_id',
            'blocked_card_msg',
            'patron_id',
            'terminal_pwd',
        ]
    ),
    '09': dict(
        label='Checkin',
        handler='checkin',
        required_fields=[
            'no_block',
            'transaction_date',
            'return_date',
            'current_location',
            'institution_id',
            'item_id',
            'terminal_pwd',
        ],
        fixed_fields=[
            'no_block',
            'transaction_date',
            'return_date',
        ],
        variable_fields=[
            'current_location',
            'institution_id',
            'item_id',
            'terminal_pwd',
            'item_properties',
            'cancel',
        ],
    ),
    '10': dict(
        label='Checkin response',
        handler='checkin_response',
        required_fields=[
            'ok',
            'resensitize',
            'magnetic_media',
            'alert',
            'transaction_date',
            'institution_id',
            'item_id',
            'permanent_location',
        ],
        fixed_fields=[
            'ok',
            'resensitize',
            'magnetic_media',
            'alert',
            'transaction_date',
        ],
        variable_fields=[
            'institution_id',
            'item_id',
            'permanent_location',
            'title_id',
            'sort_bin',
            'patron_id',
            'media_type',
            'item_properties',
            'screen_messages',
            'print_line',
        ],
    ),
    '11': dict(
        label='Checkout',
        handler='checkout',
        required_fields=[
            'sc_renewal_policy',
            'no_block',
            'transaction_date',
            'nb_due_date',
            'institution_id',
            'patron_id',
            'item_id',
            'terminal_pwd',
        ],
        fixed_fields=[
            'sc_renewal_policy',
            'no_block',
            'transaction_date',
            'nb_due_date',
        ],
        variable_fields=[
            'institution_id',
            'patron_id',
            'item_id',
            'terminal_pwd',
            'item_properties',
            'patron_pwd',
            'fee_acknowledged',
            'cancel',
        ],
    ),
    '12': dict(
        label='Checkout response',
        handler='checkout_response',
        required_fields=[
            'ok',
            'renewal_ok',
            'magnetic_media',
            'desensitize',
            'transaction_date',
            'institution_id',
            'patron_id',
            'item_id',
            'title_id',
            'due_date',
        ],
        fixed_fields=[
            'ok',
            'renewal_ok',
            'magnetic_media',
            'desensitize',
            'transaction_date',
        ],
        variable_fields=[
            'institution_id',
            'patron_id',
            'item_id',
            'title_id',
            'due_date',
            'fee_type',
            'security_inhibit',
            'currency_type',
            'fee_amount',
            'media_type',
            'item_properties',
            'transaction_id',
            'screen_messages',
            'print_line',
        ],
    ),
    '15': dict(
        label='Hold',
        handler='hold',
        required_fields=[
            'hold_mode',
            'transaction_date',
            'institution_id',
            'patron_id',
        ],
        fixed_fields=[
            'hold_mode',
            'transaction_date',
        ],
        variable_fields=[
            'expiration_date',
            'pickup_location',
            'hold_type',
            'institution_id',
            'patron_id',
            'patron_pwd',
            'item_id',
            'title_id',
            'terminal_pwd',
            'fee_acknowledged',
        ],
    ),
    '16': dict(
        label='Hold response',
        handler='hold_response',
        required_fields=[
            'ok',
            'available',
            'transaction_date',
            'institution_id',
            'patron_id',
        ],
        fixed_fields=[
            'ok',
            'available',
            'transaction_date',
        ],
        variable_fields=[
            'expiration_date',
            'queue_position',
            'pickup_location',
            'institution_id',
            'item_id',
            'title_id',
            'screen_messages',
            'print_line',
        ],
    ),
    '17': dict(
        label='Item information',
        handler='item_information',
        required_fields=[
            'transaction_date',
            'institution_id',
            'item_id',
        ],
        fixed_fields=[
            'transaction_date',
        ],
        variable_fields=[
            'institution_id',
            'item_id',
            'terminal_pwd',
        ]
    ),
    '18': dict(
        label='Item information response',
        handler='item_information_response',
        required_fields=[
            'circulation_status',
            'security_marker',
            'fee_type',
            'transaction_date',
            'item_id',
            'title_id',
        ],
        fixed_fields=[
            'circulation_status',
            'security_marker',
            'fee_type',
            'transaction_date',
        ],
        variable_fields=[
            'hold_queue_length',
            'due_date',
            'recall_date',
            'hold_pickup_date',
            'item_id',
            'title_id',
            'owner',
            'currency_type',
            'fee_amount',
            'media_type',
            'permanent_location',
            'current_location',
            'item_properties',
            'screen_messages',
            'print_line',
        ],
    ),
    '19': dict(
        label='Item status update',
        handler='item_status_update',
        required_fields=[
            'transaction_date',
            'institution_id',
            'item_id',
            'item_properties',
        ],
        fixed_fields=[
            'transaction_date',
        ],
        variable_fields=[
            'institution_id',
            'item_id',
            'terminal_pwd',
            'item_properties'
        ],
    ),
    '20': dict(
        label='Item status update response',
        handler='item_status_update_response',
        required_fields=[
            'item_properties_ok',
            'transaction_date',
        ],
        fixed_fields=[
            'item_properties_ok',
            'transaction_date',
        ],
        variable_fields=[
            'item_id',
            'title_id',
            'item_properties',
            'screen_messages',
            'print_line',
        ],
    ),
    '23': dict(
        label='Patron status',
        handler='patron_status',
        required_fields=[
            'language',
            'transaction_date',
            'institution_id',
            'patron_id',
            'terminal_pwd',
            'patron_pwd',
        ],
        fixed_fields=[
            'language',
            'transaction_date',
        ],
        variable_fields=[
            'institution_id',
            'patron_id',
            'terminal_pwd',
            'patron_pwd',
        ],
    ),
    '24': dict(
        label='Patron status response',
        handler='patron_status_response',
        required_fields=[
            'patron_status',
            'language',
            'transaction_date',
        ],
        fixed_fields=[
            'patron_status',
            'language',
            'transaction_date',
        ],
        variable_fields=[
            'institution_id',
            'patron_id',
            'patron_name',
            'valid_patron',
            'valid_patron_pwd',
            'currency_type',
            'fee_amount',
            'screen_messages',
            'print_line',
        ],
    ),
    '25': dict(
        label='Patron enable',
        handler='patron_enable',
        required_fields=[
            'transaction_date',
            'institution_id',
            'patron_id',
        ],
        fixed_fields=[
            'transaction_date',
        ],
        variable_fields=[
            'institution_id',
            'patron_id',
            'terminal_pwd',
            'patron_pwd',
        ],
    ),
    '26': dict(
        label='Patron enable response',
        handler='patron_enable_response',
        required_fields=[
            'patron_status',
            'language',
            'transaction_date',
            'institution_id',
            'patron_id',
            'patron_name',
        ],
        fixed_fields=[
            'patron_status',
            'language',
            'transaction_date',
        ],
        variable_fields=[
            'institution_id',
            'patron_id',
            'patron_name',
            'valid_patron',
            'valid_patron_pwd',
            'screen_messages',
            'print_line',
        ],
    ),
    '29': dict(
        label='Renew',
        handler='renew',
        required_fields=[
            'third_party_allowed',
            'no_block',
            'nb_due_date',
            'transaction_date',
            'institution_id',
            'patron_id',
        ],
        fixed_fields=[
            'third_party_allowed',
            'no_block',
            'nb_due_date',
            'transaction_date',
        ],
        variable_fields=[
            'institution_id',
            'patron_id',
            'patron_pwd',
            'item_id',
            'title_id',
            'terminal_pwd',
            'item_properties',
            'fee_acknowledged',
        ],
    ),
    '30': dict(
        label='Renew response',
        handler='renew_response',
        required_fields=[
            'ok',
            'renewal_ok',
            'magnetic_media',
            'desensitize',
            'transaction_date',
            'institution_id',
            'patron_id',
            'item_id',
            'title_id',
            'due_date',
        ],
        fixed_fields=[
            'ok',
            'renewal_ok',
            'magnetic_media',
            'desensitize',
            'transaction_date',
        ],
        variable_fields=[
            'institution_id',
            'patron_id',
            'item_id',
            'title_id',
            'due_date',
            'fee_type',
            'security_inhibit',
            'currency_type',
            'fee_amount',
            'media_type',
            'item_properties',
            'transaction_id',
            'screen_messages',
            'print_line',
        ],
    ),
    '35': dict(
        label='End patron session',
        handler='end_patron_session',
        required_fields=[
            'transaction_date',
            'institution_id',
            'patron_id',
        ],
        fixed_fields=[
            'transaction_date',
        ],
        variable_fields=[
            'institution_id',
            'patron_id',
            'terminal_pwd',
            'patron_pwd',
        ],
    ),
    '36': dict(
        label='End session response',
        handler='end_session_response',
        required_fields=[
            'end_session',
            'transaction_date',
            'institution_id',
            'patron_id',
        ],
        fixed_fields=[
            'end_session',
            'transaction_date',
        ],
        variable_fields=[
            'institution_id',
            'patron_id',
            'screen_messages',
            'print_line',
        ],
    ),
    '37': dict(
        label='Fee paid',
        handler='fee_paid',
        required_fields=[
            'transaction_date',
            'fee_type',
            'payment_type',
            'currency_type',
            'fee_amount',
            'institution_id',
            'patron_id',
            'terminal_pwd',
            'patron_pwd',
        ],
        fixed_fields=[
            'transaction_date',
            'fee_type',
            'payment_type',
            'currency_type',
        ],
        variable_fields=[
            'fee_amount',
            'institution_id',
            'patron_id',
            'terminal_pwd',
            'patron_pwd',
            'fee_id',
            'transaction_id'
        ]
    ),
    '38': dict(
        label='Fee paid response',
        handler='fee_paid_response',
        required_fields=[
            'transaction_date',
            'payment_accepted',
            'institution_id',
            'patron_id',
        ],
        fixed_fields=[
            'transaction_date',
            'payment_accepted',
        ],
        variable_fields=[
            'institution_id',
            'patron_id',
            'transaction_id',
            'screen_messages',
            'print_line',
        ],
    ),
    '63': dict(
        label='Patron information',
        handler='patron_information',
        required_fields=[
            'language',
            'transaction_date',
            'summary',
            'institution_id',
            'patron_id',
        ],
        fixed_fields=[
            'language',
            'transaction_date',
            'summary',
        ],
        variable_fields=[
            'institution_id',
            'patron_id',
            'terminal_pwd',
            'patron_pwd',
            'start_item',
            'end_item'
        ],
    ),
    '64': dict(
        label='Patron information response',
        handler='patron_information',
        required_fields=[
            'patron_status',
            'language',
            'transaction_date',
            'hold_items_count',
            'overdue_items_count',
            'charged_items_count',
            'fine_items_count',
            'recall_items_count',
            'unavailable_holds_count',
            'institution_id',
            'patron_id',
            'patron_name',
        ],
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
        variable_fields=[
            'institution_id',
            'patron_id',
            'patron_name',
            'home_address',
            'home_phone',
            'email',
            'hold_items_limit',
            'overdue_items_limit',
            'charged_items_limit',
            'hold_items',
            'overdue_items',
            'fine_items',
            'charged_items',
            'recall_items',
            'unavailable_hold_items',
            'valid_patron',
            'valid_patron_pwd',
            'currency_type',
            'fee_amount',
            'fee_limit',
            'screen_messages',
            'print_line',
        ],
    ),
    '65': dict(
        label='Renew all',
        handler='renew_all',
        required_fields=[
            'transaction_date',
        ],
        fixed_fields=[
            'transaction_date',
        ],
        variable_fields=[
            'institution_id',
            'patron_id',
            'patron_pwd',
            'terminal_pwd',
            'fee_acknowledged',
        ],
    ),
    '66': dict(
        label='Renew all response',
        handler='renew_all_response',
        required_fields=[
            'ok',
            'renewed_count',
            'unrenewed_count',
            'transaction_date',
        ],
        fixed_fields=[
            'ok',
            'renewed_count',
            'unrenewed_count',
            'transaction_date',
        ],
        variable_fields=[
            'institution_id',
            'renewed_items',
            'unrenewed_items',
            'screen_messages',
            'print_line',
        ],
    ),
    '93': dict(
        label='Login',
        handler='login',
        required_fields=[
            'uid_algorithm',
            'pwd_algorithm',
            'login_uid',
            'login_pwd',
        ],
        fixed_fields=[
            'uid_algorithm',
            'pwd_algorithm',
        ],
        variable_fields=[
            'login_uid',
            'login_pwd',
            'location_code',
        ],
    ),
    '94': dict(
        label='Login response',
        required_fields=[
            'ok'
        ],
        fixed_fields=[
            'ok'
        ],
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
        required_fields=[
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
            'institution_id',
            'supported_messages',
        ],
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
        variable_fields=[
            'institution_id',
            'library_name',
            'supported_messages',
            'terminal_location',
            'screen_messages',
            'print_line',
        ],
    ),
    '99': dict(
        label='Selfcheck status',
        handler='selfcheck_status',
        required_fields=[
            'status_code',
            'max_print_width',
            'protocol_version',
        ],
        fixed_fields=[
            'status_code',
            'max_print_width',
            'protocol_version',
        ],
    ),
}

# Define fixed fields
SIP2_FIXED_FIELD_DEFINITION = dict(
    available=dict(length=1, label=_('available'),
                   callback=convert_bool_to_char),
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
    end_session=dict(length=1, label=_('End Session'),
                     callback=convert_bool_to_char),
    summary=dict(length=10, label=_('summary')),
    hold_mode=dict(length=1, label=_('hold mode')),
    hold_items_count=dict(length=4, fill='0', label=_('hold items count')),
    overdue_items_count=dict(length=4, fill='0',
                             label=_('overdue items count')),
    charged_items_count=dict(length=4, fill='0',
                             label=_('charged items count')),
    fine_items_count=dict(length=4, fill='0', label=_('fine items count')),
    recall_items_count=dict(length=4, fill='0', label=_('recall items count')),
    unavailable_holds_count=dict(length=4, fill='0',
                                 label=_('unavailable holds count')),
    sc_renewal_policy=dict(length=1, label=_('sc renewal policy')),
    no_block=dict(length=1, label=_('no block')),
    card_retained=dict(length=1, label=_('card retained')),
    nb_due_date=dict(length=18, label=_('nb due date')),
    third_party_allowed=dict(length=1, label=_('Third party allowed')),
    renewal_ok=dict(length=1, label=_('renewal ok'),
                    callback=convert_bool_to_char),
    unrenewed_count=dict(length=4, label=_('renewal ok')),
    renewed_count=dict(length=4, label=_('renewal ok')),
    magnetic_media=dict(length=1, label=_('magnetic media'),
                        callback=convert_to_char),
    desensitize=dict(length=1, label=_('desensitize'),
                     callback=convert_to_char),
    resensitize=dict(length=1, label=_('resensitize'),
                     callback=convert_bool_to_char),
    return_date=dict(length=18, label=_('return date')),
    alert=dict(length=1, label=_('alert'), callback=convert_bool_to_char),
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

# Define variable fields
SIP2_VARIABLE_FIELD_DEFINITION = dict(
    patron_id=dict(field_id='AA', label=_('patron identifier')),
    item_id=dict(field_id='AB', label=_('item identifier')),
    terminal_pwd=dict(field_id='AC', label=_('terminal password')),
    patron_pwd=dict(field_id='AD', label=_('patron password')),
    patron_name=dict(field_id='AE', label=_('personal name')),
    screen_messages=dict(field_id='AF', multiple=True,
                         label=_('screen message')),
    print_line=dict(field_id='AG', multiple=True, label=_('print line')),
    due_date=dict(field_id='AH', label=_('due date'),
                  callback=parse_circulation_date),
    title_id=dict(field_id='AJ', label=_('title identifier')),
    blocked_card_msg=dict(field_id='AL', label=_('blocked card msg')),
    library_name=dict(field_id='AM', label=_('library name')),
    terminal_location=dict(field_id='AN', label=_('terminal location')),
    institution_id=dict(field_id='AO', label=_('institution id')),
    current_location=dict(field_id='AP', label=_('current location')),
    permanent_location=dict(field_id='AQ', label=_('permanent location')),
    hold_items=dict(field_id='AS', multiple=True, label=_('hold items')),
    overdue_items=dict(field_id='AT', multiple=True, label=_('overdue items')),
    charged_items=dict(field_id='AU', multiple=True, label=_('charged items')),
    fine_items=dict(field_id='AV', multiple=True, label=_('fine items')),
    sequence_number=dict(field_id='AY', length=1, label=_('sequence number')),
    checksum=dict(field_id='AZ', length=4, label=_('checksum')),
    home_address=dict(field_id='BD', label=_('home address')),
    email=dict(field_id='BE', label=_('e-mail address')),
    home_phone=dict(field_id='BF', label=_('home phone number')),
    owner=dict(field_id='BG', label=_('owner')),
    currency_type=dict(field_id='BH', length=3, label=_('currency type')),
    cancel=dict(field_id='BI', length=1, label=_('cancel')),
    transaction_id=dict(field_id='BK', label=_('transaction id')),
    valid_patron=dict(field_id='BL', length=1, label=_('valid patron'),
                      callback=convert_bool_to_char),
    renewed_items=dict(field_id='BM', multiple=True, label=_('renewed items')),
    unrenewed_items=dict(field_id='BN', multiple=True,
                         label=_('unrenewed items')),
    fee_acknowledged=dict(field_id='BO', length=1,
                          label=_('fee acknowledged')),
    start_item=dict(field_id='BP', label=_('start item')),
    end_item=dict(field_id='BQ', label=_('end item')),
    queue_position=dict(field_id='BR', label=_('queue position')),
    pickup_location=dict(field_id='BS', label=_('pickup location')),
    fee_type=dict(field_id='BT', length=2, label=_('fee type')),
    recall_items=dict(field_id='BU', multiple=True, label=_('recall items')),
    fee_amount=dict(field_id='BV', label=_('fee amount')),
    expiration_date=dict(field_id='BW', length=18, label=_('expiration date')),
    supported_messages=dict(field_id='BX', label=_('supported messages')),
    hold_type=dict(field_id='BY', length=1, label=_('hold type')),
    hold_items_limit=dict(field_id='BZ', length=4, fill='0',
                          label=_('hold items limit')),
    overdue_items_limit=dict(field_id='CA', length=4, fill='0',
                             label=_('overdue items limit')),
    charged_items_limit=dict(field_id='CB', length=4, fill='0',
                             label=_('charged items limit')),
    fee_limit=dict(field_id='CC', label=_('fee limit')),
    unavailable_hold_items=dict(field_id='CD', multiple=True,
                                label=_('unavailable hold items')),
    hold_queue_length=dict(field_id='CF', label=_('hold queue length')),
    fee_id=dict(field_id='CG', label=_('fee identifier')),
    item_properties=dict(field_id='CH', label=_('item properties')),
    security_inhibit=dict(field_id='CI', length=1,
                          label=_('security inhibit')),
    recall_date=dict(field_id='CJ', length=18, label=_('recall date')),
    media_type=dict(field_id='CK', length=3, label=_('media type'),
                    callback=get_media_type),
    sort_bin=dict(field_id='CL', label=_('sort bin')),
    hold_pickup_date=dict(field_id='CM', length=18,
                          label=_('hold pickup date')),
    login_uid=dict(field_id='CN', label=_('login user id')),
    login_pwd=dict(field_id='CO', label=_('login password')),
    location_code=dict(field_id='CP', label=_('location code')),
    valid_patron_pwd=dict(field_id='CQ', length=1,
                          label=_('valid patron password'),
                          callback=convert_bool_to_char),
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
)
