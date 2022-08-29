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

"""Models for Invenio-SIP2."""

from enum import Enum

from invenio_sip2.proxies import current_sip2 as acs_system


class SupportedMessages:
    """Class to define supported mesages from handler config."""

    handlers = [
        'patron_status',
        'checkout',
        'checkin',
        'block_patron',
        'system_status',
        'request_resend',
        'login',
        'account',
        'end_patron_session',
        'fee_paid',
        'item',
        'item_status_update',
        'enable_patron',
        'hold',
        'renew',
        'renew_all',
    ]

    def __init__(self):
        """Constructor."""
        self.supported_messages = {
            'request_resend': True,
            'end_patron_session': True,
        }

    def __str__(self):
        """Sip2 string representation."""
        supported_messages_text = ''
        for handler in self.handlers:
            supported_messages_text += 'Y' \
                if handler in self.supported_messages else 'N'
        return supported_messages_text

    def add_supported_message(self, handler):
        """Add supported message."""
        if handler in self.handlers:
            self.supported_messages[handler] = True


class PatronStatusTypes(Enum):
    """Enum class to list all possible patron status types."""

    CHARGE_PRIVILEGES_DENIED = 'charge_privileges_denied'
    RENEWAL_PRIVILEGES_DENIED = 'renewal_privileges_denied'
    RECALL_PRIVILEGES_DENIED = 'recall_privileges_denied'
    HOLD_PRIVILEGES_DENIED = 'hold_privileges_denied'
    CARD_REPORTED_LOST = 'card_reported_lost'
    TOO_MANY_ITEMS_CHARGED = 'too_many_items_charged'
    TOO_MANY_ITEMS_OVERDUE = 'too_many_items_overdue'
    TOO_MANY_RENEWALS = 'too_many_renewals'
    TOO_MANY_CLAIMS_OF_ITEMS_RETURNED = 'too_many_claims_of_items_returned'
    TOO_MANY_ITEMS_LOST = 'too_many_items_lost'
    EXCESSIVE_OUTSTANDING_FINES = 'excessive_outstanding_fines'
    EXCESSIVE_OUTSTANDING_FEES = 'excessive_outstanding_fees'
    RECALL_OVERDUE = 'recall_overdue'
    TOO_MANY_ITEMS_BILLED = 'too_many_items_billed'


class PatronStatus(object):
    """Class to define patron status."""

    def __init__(self):
        """Constructor."""
        self.patron_status_types = {}

    def __str__(self):
        """Sip2 string representation."""
        patron_status_text = ''
        for status_type in PatronStatusTypes:
            patron_status_text += 'Y' \
                if self.patron_status_types.get(status_type) else ' '
        return patron_status_text

    def add_patron_status_type(self, patron_status_type):
        """Add patron status.

        :param patron_status_type: Enum of patron status type

        Add ``patron_status_type`` indicates that the condition is true.
        raise exception if patron status type does not exist.
        """
        if patron_status_type not in PatronStatusTypes:
            raise Exception(msg='patron status type does not exist')

        self.patron_status_types[patron_status_type] = True


class SelfcheckEnablePatron(dict):
    """Class representing patron information handler response."""

    def __init__(self, patron_id, institution_id, patron_name='',
                 patron_status=None, language='und', **kwargs):
        """Constructor.

        :param patron_id - patron identifier (e.g. id, barcode, ...)
        :param institution_id - institution id (or code) of the patron
        :param patron_name - full name of the patron
        :param patron_status - status of the patron
        :param language - iso-639-2 language
        :param kwargs - optional fields
        """
        # required properties
        self['patron_id'] = patron_id
        self['patron_name'] = patron_name
        self['patron_status'] = patron_status or PatronStatus()
        self['institution_id'] = institution_id
        self['language'] = language
        self['screen_messages'] = []

        # optional properties
        for key, value in kwargs.items():
            if value:
                self[key] = value


class SelfcheckPatronStatus(dict):
    """Class representing patron information handler response."""

    def __init__(self, patron_id, institution_id, patron_name='',
                 patron_status=None, language='und', **kwargs):
        """Constructor.

        :param patron_id - patron identifier (e.g. id, barcode, ...)
        :param institution_id - institution id (or code) of the patron
        :param patron_name - full name of the patron
        :param patron_status - status of the patron
        :param language - iso-639-2 language
        :param kwargs - optional fields
        """
        # required properties
        self['patron_id'] = patron_id
        self['patron_name'] = patron_name
        self['patron_status'] = patron_status or PatronStatus()
        self['institution_id'] = institution_id
        self['language'] = language
        self['screen_messages'] = []

        # optional properties
        for key, value in kwargs.items():
            if value:
                self[key] = value


class SelfcheckPatronInformation(dict):
    """Class representing patron information handler response."""

    def __init__(self, patron_id, institution_id, patron_name='',
                 patron_status=None, language='und', **kwargs):
        """Constructor.

        :param patron_id - patron identifier (e.g. id, barcode, ...)
        :param institution_id - institution id (or code) of the patron
        :param patron_name - full name of the patron
        :param patron_status - status of the patron
        :param language - iso-639-2 language
        :param kwargs - optional fields
        """
        # required properties
        self['patron_id'] = patron_id
        self['patron_name'] = patron_name
        self['patron_status'] = patron_status or PatronStatus()
        self['institution_id'] = institution_id
        self['language'] = language
        self['hold_items'] = []
        self['overdue_items'] = []
        self['charged_items'] = []
        self['fine_items'] = []
        self['recall_items'] = []
        self['unavailable_items'] = []
        self['screen_messages'] = []

        # optional properties
        for key, value in kwargs.items():
            if value:
                self[key] = value

    @property
    def patron_id(self):
        """Shortcut for patron pid."""
        return self.get('patron_id')

    @property
    def patron_name(self):
        """Shortcut for patron pid."""
        return self.get('patron_name')

    @property
    def hold_items_count(self):
        """Shortcut for hold items count."""
        return len(self.get('hold_items', []))

    @property
    def overdue_items_count(self):
        """Shortcut for overdue items count."""
        return len(self.get('overdue_items', []))

    @property
    def charged_items_count(self):
        """Shortcut for charged items count."""
        return len(self.get('charged_items', []))

    @property
    def fine_items_count(self):
        """Shortcut for fine items count."""
        return len(self.get('fine_items', []))

    @property
    def recall_items_count(self):
        """Shortcut for recall items count."""
        return len(self.get('recall_items', []))

    @property
    def unavailable_items_count(self):
        """Shortcut for unavailable items count."""
        return len(self.get('unavailable_items', []))


class SelfcheckItemInformation(dict):
    """Class representing item information handler response."""

    def __init__(self, item_id, title_id=None, circulation_status=None,
                 fee_type=None, security_marker=None, **kwargs):
        """Constructor.

        :param patron_id - patron identifier (e.g. id, barcode, ...)
        :param patron_name - full name of the patron
        :param institution_id - institution id (or code) of the patron
        :param language - iso-639-2 language
        :param kwargs - optional fields
        """
        # required properties
        self['item_id'] = item_id
        self['title_id'] = title_id or ''
        self['circulation_status'] = circulation_status or \
            SelfcheckCirculationStatus.OTHER
        self['fee_type'] = fee_type or SelfcheckFeeType.OTHER
        self['security_marker'] = security_marker or \
            SelfcheckSecurityMarkerType.OTHER
        self['screen_messages'] = []

        # optional properties
        for key, value in kwargs.items():
            if value:
                self[key] = value


class SelfcheckCheckin(dict):
    """Class representing checkin handler response."""

    def __init__(self, permanent_location, checkin=False, alert=False,
                 magnetic_media='unknown', resensitize='unknown',  **kwargs):
        """Constructor.

        :param permanent_location - permanent_location of the item
        :param checkin - checkin operation is success or not
        :param alert - indicate if the selcheck will generate sound alert
        :param magnetic_media - indicate the presence of magnetic media
        :param resensitize - resensitize an item ?
        :param kwargs - optional fields
        """
        # required properties
        self['checkin'] = checkin
        self['alert'] = alert
        self['magnetic_media'] = magnetic_media
        self['resensitize'] = resensitize
        self['permanent_location'] = permanent_location
        self['screen_messages'] = []

        # optional properties
        for key, value in kwargs.items():
            if value:
                self[key] = value

    @property
    def is_success(self):
        """Shortcut for checkin."""
        return self.get('checkin')

    @property
    def resensitize(self):
        """Shortcut for resensitize."""
        return self.get('resensitize')

    @property
    def has_magnetic_media(self):
        """Shortcut for desensitize."""
        return self.get('magnetic_media')

    @property
    def sound_alert(self):
        """Shortcut for alert."""
        return self.get('alert')


class SelfcheckCheckout(dict):
    """Class representing checkout handler response."""

    def __init__(self, title_id, checkout=False, renewal=False,
                 magnetic_media='unknown', desensitize='unknown',  **kwargs):
        """Constructor.

        :param title_id - title_id (e.g. title, identifier, ...)
        :param checkout - checkout operation is success or not
        :param renewal - renewal operation is success or not
        :param magnetic_media - indicate the presence of magnetic media
        :param desensitize - desensitize an item ?
        :param kwargs - optional fields
        """
        # required properties
        self['checkout'] = checkout
        self['renewal'] = renewal
        self['magnetic_media'] = magnetic_media
        self['desensitize'] = desensitize
        self['title_id'] = title_id
        self['screen_messages'] = []

        # optional properties
        for key, value in kwargs.items():
            if value:
                self[key] = value

    @property
    def is_success(self):
        """Shortcut for checkout ok."""
        return self.get('checkout')

    @property
    def is_renewal(self):
        """Shortcut for renewal ok."""
        return self.get('renewal')

    @property
    def due_date(self):
        """Shortcut for due date."""
        return self.get('due_date', '')

    @property
    def desensitize(self):
        """Shortcut for desensitize."""
        return self.get('desensitize')

    @property
    def has_magnetic_media(self):
        """Shortcut for desensitize."""
        return self.get('magnetic_media')


class SelfcheckHold(dict):
    """Class representing hold handler response."""

    def __init__(self, hold=False, available=False, **kwargs):
        """Constructor.

        :param hold - hold operation is success or not
        :param available - item available or not
        :param kwargs - optional fields
        """
        # required properties
        self['hold'] = hold
        self['available'] = available
        self['screen_messages'] = []

        # optional properties
        for key, value in kwargs.items():
            if value:
                self[key] = value

    @property
    def is_success(self):
        """Shortcut for hold ok."""
        return self.get('hold')

    @property
    def is_available(self):
        """Shortcut for available."""
        return self.get('available')


class SelfcheckRenew(dict):
    """Class representing renew handler response."""

    def __init__(self, title_id, success=False, renewal=False,
                 magnetic_media='unknown', desensitize='unknown',  **kwargs):
        """Constructor.

        :param title_id: title_id (e.g. title, identifier, ...)
        :param renew: renew operation is success or not
            should be set to True if the ACS renew the item.
            should be set to 0 if the ACS did not renew the item.
        :param renewal: renewal operation.
            should be set to True if the patron requesting to renew the item
            already has the item renewed.
            should be set to False if the item is not already renewed.
        :param magnetic_media: indicate the presence of magnetic media
        :param desensitize: desensitize an item ?
        :param kwargs: optional fields
        """
        # required properties
        self['success'] = success
        self['renewal'] = renewal
        self['magnetic_media'] = magnetic_media
        self['desensitize'] = desensitize
        self['title_id'] = title_id
        self['due_date'] = acs_system.sip2_current_date
        self['screen_messages'] = []

        # optional properties
        for key, value in kwargs.items():
            if value:
                self[key] = value

    @property
    def is_success(self):
        """Shortcut for success operation."""
        return self.get('success')

    @property
    def is_renewal(self):
        """Shortcut for renewal ok."""
        return self.get('renewal')

    @property
    def due_date(self):
        """Shortcut for due date."""
        return self.get('due_date', '')

    @property
    def desensitize(self):
        """Shortcut for desensitize."""
        return self.get('desensitize')

    @property
    def has_magnetic_media(self):
        """Shortcut for desensitize."""
        return self.get('magnetic_media')


class SelfcheckLanguage(Enum):
    """Enum class to list all available language."""

    # SIP2 supported Language
    UNKNOWN = '000'
    ENGLISH = '001'
    FRENCH = '002'
    GERMAN = '003'
    ITALIAN = '004'
    DUTCH = '005'
    SWEDISH = '006'
    FINNISH = '007'
    SPANISH = '008'
    DANISH = '009'
    PORTUGUESE = '010'
    CANADIAN_FRENCH = '011'
    NORWEGIAN = '012'
    HEBREW = '013'
    JAPANESE = '014'
    RUSSIAN = '015'
    ARABIC = '016'
    POLISH = '017'
    GREEK = '018'
    CHINESE = '019'
    KOREAN = '020'
    NORTH_AMERICAN_SPANISH = '021'
    TAMIL = '022'
    MALAY = '023'
    UNITED_KINGDOM = '024'
    ICELANDIC = '025'
    BELGIAN = '026'
    TAIWANESE = '027'

    # ISO 639-2 common Language mapping
    und = UNKNOWN
    eng = ENGLISH
    fre = FRENCH
    fra = FRENCH
    ger = GERMAN
    ita = ITALIAN
    dut = DUTCH
    swe = SWEDISH
    fin = FINNISH
    spa = SPANISH
    dan = DANISH
    por = PORTUGUESE
    nor = NORWEGIAN
    heb = HEBREW
    jpn = JAPANESE
    rus = RUSSIAN
    pol = POLISH
    gre = GREEK
    chi = CHINESE
    zho = CHINESE
    kor = KOREAN
    tam = TAMIL
    may = MALAY
    msa = MALAY
    ice = ICELANDIC
    isl = ICELANDIC


class SelfcheckSecurityMarkerType(object):
    """Class to handle all available security marker type."""

    OTHER = '00'
    NONE = '01'
    TATTLE_TAPE_SECURITY_STRIP = '02'
    WHISPHER_TAPE = '03'


class SelfcheckFeeType(object):
    """Class to handle all available fee type."""

    OTHER = '01'
    ADMINISTRATIVE = '02'
    DAMAGE = '03'
    OVERDUE = '04'
    PROCESSING = '05'
    RENTAL = '06'
    REPLACEMENT = '07'
    COMPUTER_ACCESS_CHARGE = '08'
    HOLD_FEE = '09'


class SelfcheckMediaType(object):
    """Class to handle all available media type."""

    OTHER = '000'
    BOOK = '001'
    MAGAZINE = '002'
    BOUND_JOURNAL = '003'
    AUDIO = '004'
    VIDEO = '005'
    CD_OR_CDROM = '006'
    DISKETTE = '007'
    BOOK_WHIT_DISKETTE = '008'
    BOOK_WHIT_CD = '009'
    BOOK_WHIT_AUDIO_TAPE = '010'


class SelfcheckCirculationStatus(object):
    """Class to handle all available circulation status of an item."""

    OTHER = '01'
    ON_ORDER = '02'
    AVAILABLE = '03'
    CHARGED = '04'
    CHARGED_RECALL = '05'  # not to be recalled until earliest recall date
    IN_PROCESS = '06'
    RECALLED = '07'
    WAITING_ON_HOLD_SHELF = '08'
    WAITING_TO_RESHELF = '09'
    IN_TRANSIT = '10'
    CLAIMED_RETURNED = '11'
    LOST = '12'
    MISSING = '13'


class SelfcheckSummary:
    """Class representing summary."""

    fields = [
        'hold_items',
        'overdue_items',
        'charged_items',
        'fine_items',
        'recall_items',
        'unavailable_items',
    ]

    def __init__(self, text):
        """Init."""
        from .utils import decode_char_to_bool
        self.hold_items = decode_char_to_bool(text[0:])
        self.overdue_items = decode_char_to_bool(text[1])
        self.charged_items = decode_char_to_bool(text[2])
        self.fine_items = decode_char_to_bool(text[3])
        self.recall_items = decode_char_to_bool(text[4])
        self.unavailable_items = decode_char_to_bool(text[5])

    def is_needed(self, key):
        """Check if the given information is needed."""
        return hasattr(self, key)
