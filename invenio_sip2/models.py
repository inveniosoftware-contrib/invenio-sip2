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


class SelfcheckClient(dict):
    """class for user client."""

    def __init__(self, address, remote_app):
        """Constructor.

        :param address: 2-tuple (host, port)
        :param remote_app: remote app)
        """
        self['ip_address'] = address[0]
        self['socket_port'] = address[1]
        self['remote_app'] = remote_app
        self['authenticated'] = False

    def update(self, data):
        """Update instance with dictionary data.

        :param data: Dict with user metadata.
        """
        super(SelfcheckClient, self).update(data)

    @property
    def is_authenticated(self):
        """Shortcut to check if the selfcheck client is authenticated."""
        return self.get('authenticated')

    @property
    def remote_app(self):
        """Shortcut to remote application."""
        return self.get('remote_app')

    @property
    def institution_id(self):
        """Shortcut to institution id."""
        return self.get('institution_id')

    @property
    def library_name(self):
        """Shortcut to library name."""
        return self.get('library_name')

    @classmethod
    def get_user_client_by_id(cls, client_id):
        """Get client by id."""
        from .server import SocketServer
        return SocketServer.get_client(client_id)


class SelfcheckPatronStatusTypes(Enum):
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


class SelfcheckPatronStatus(object):
    """Class to define patron status."""

    patron_status_types = {}

    def __str__(self):
        """Sip2 string representation."""
        patron_status_text = ''
        for status_type in SelfcheckPatronStatusTypes:
            patron_status_text += 'Y' \
                if self.patron_status_types.get(status_type) else ' '
        return patron_status_text

    def add_patron_status_type(self, patron_status_type):
        """Add patron status.

        :param patron_status_type: Enum of patron status type

        Add ``patron_status_type`` indicates that the condition is true.
        raise exception if patron status type does not exist.
        """
        if patron_status_type not in SelfcheckPatronStatusTypes:
            raise Exception(msg='patron status type does not exist')

        self.patron_status_types[patron_status_type] = True


class SelfcheckPatronInformation(dict):
    """Class representing patron information."""

    def __init__(self, patron_id, patron_name, institution_id,
                 language, **kwargs):
        """Constructor.

        :param patron_id - patron identifier (e.g. id, barcode, ...)
        :param patron_name - full name of the patron
        :param institution_id - institution id (or code) of the patron
        :param language - iso-639-2 language
        :param kwargs - optional fields
        """
        # required properties
        self['patron_id'] = patron_id
        self['patron_name'] = patron_name
        self['patron_status'] = SelfcheckPatronStatus()
        self['institution_id'] = institution_id
        self['language'] = language
        self['hold_items'] = []
        self['overdue_items'] = []
        self['charged_items'] = []
        self['fine_items'] = []
        self['recall_items'] = []
        self['unavailable_items'] = []

        # optional properties
        for key, value in kwargs.items():
            if value:
                self[key] = value

    @property
    def patron_id(self):
        """Shortcut for patron pid."""
        return self.get('patron_id')

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
    kor = KOREAN
    tam = TAMIL
    may = MALAY
    ice = ICELANDIC
