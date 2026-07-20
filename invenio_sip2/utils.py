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

"""Invenio-SIP2 Utilities."""

from datetime import datetime

import pytz
from dateutil import parser
from flask import current_app
from pycountry import languages

from invenio_sip2.models import (
    SelfcheckCirculationStatus,
    SelfcheckLanguage,
    SelfcheckMediaType,
    SelfcheckSecurityMarkerType,
)
from invenio_sip2.proxies import current_logger as logger
from invenio_sip2.proxies import current_sip2 as acs_system


def convert_bool_to_char(value=False):
    """Convert boolean to SIP2 char representation."""
    return "Y" if value else "N"


def convert_to_char(value="unknown"):
    """Convert value to SIP2 char representation."""
    if isinstance(value, str):
        return "U"
    return "Y" if value else "N"


def decode_char_to_bool(value="N"):
    """Decode SIP2 char representation to boolean."""
    return value == "Y"


def parse_circulation_date(date):
    """Converts a date of string format to a formatted date utc aware."""
    date_format = current_app.config.get("SIP2_CIRCULATION_DATE_FORMAT")
    try:
        if isinstance(date, datetime):
            if date.tzinfo is None:
                date = date.replace(tzinfo=pytz.utc)
            return date.strftime(date_format)
        return date_string_to_utc(date).strftime(date_format)
    except (ValueError, AttributeError):
        logger.warning(f"parse circulation date error for: [{date}]")
        return date or ""


def date_string_to_utc(date):
    """Converts a date of string format to a datetime utc aware."""
    parsed_date = parser.parse(date)
    if parsed_date.tzinfo:
        return parsed_date
    return pytz.utc.localize(parsed_date)


def get_language_code(language):
    """Get mapped selfcheck language.

    :param language: ISO 639-2 common language
    :returns SIP2 mapped language code
    """
    try:
        return SelfcheckLanguage[language].value
    except KeyError:
        return SelfcheckLanguage.UNKNOWN.value


def ensure_i18n_language(language):
    """Ensure that the given language is an i18n language."""
    if len(language) > 2:
        return languages.lookup(language).alpha_2
    return language


def get_security_marker_type(marker_type=None):
    """Get mapped security marker type."""
    try:
        return getattr(SelfcheckSecurityMarkerType, marker_type)
    except AttributeError:
        return current_app.config.get("SIP2_DEFAULT_SECURITY_MARKER")


def get_media_type(media_type=None):
    """Get mapped circulation status."""
    try:
        return getattr(SelfcheckMediaType, media_type)
    except AttributeError:
        return SelfcheckMediaType.OTHER


def get_circulation_status(status=None):
    """Get mapped circulation status."""
    try:
        return getattr(SelfcheckCirculationStatus, status)
    except AttributeError:
        return SelfcheckCirculationStatus.OTHER


#: SIP2 variable field identifiers carrying credentials (terminal password,
#: patron password and login password) that must be masked before logging.
SENSITIVE_FIELD_IDS = ("AC", "AD", "CO")


def mask_sensitive_data(message_str):
    """Mask credential fields in a raw SIP2 message before logging.

    SIP2 request messages embed passwords (fields "AC", "AD" and "CO") in
    clear text. This replaces their value so logs and error reports never
    expose them.

    :param message_str: raw SIP2 string message
    :returns: message with the value of sensitive fields replaced by "****"
    """
    parts = message_str.split("|")
    for index, part in enumerate(parts):
        if part[:2] in SENSITIVE_FIELD_IDS and len(part) > 2:
            parts[index] = f"{part[:2]}****"
    return "|".join(parts)


def generate_checksum(message):
    """Generate and format checksum for SIP2 messages.

    :param message: SIP2 string message
    :returns checksum string
    """
    # Calculate checksum
    checksum = sum(message.encode(acs_system.text_encoding))
    return format((-checksum & 0xFFFF), "X")


def verify_checksum(message_str):
    """Verify the integrity of SIP2 messages containing checksum.

    :param message_str: SIP2 string message
    :returns boolean
    """
    # extract message without checksum
    message = message_str[:-4]
    # extract and parse checksum
    checksum = int(message_str[-4:], 16)

    # check minimum length of message
    # It should be 8 for request ACS resend and 11 for all other messaged
    minimum_len = 8 if message_str[:2] == "97" else 11
    if len(message_str) < minimum_len:
        return False

    # SIP2 clients disagree on how to sum non-ASCII characters: some sum
    # the encoded bytes, others sum the Unicode code points. Both agree on
    # ASCII but diverge on multi-byte characters (e.g. "€"), so accept the
    # message if either interpretation validates. The two's complement of the
    # summed value plus the checksum should equal zero for a valid message.
    for value in (
        sum(message.encode(acs_system.text_encoding)),
        sum(ord(char) for char in message),
    ):
        if -(value + checksum) & 0xFFFF == 0:
            return True
    return False


def verify_sequence_number(client, message):
    """Check sequence number increment.

    :param client: connected client
    :param message: instance of Message object
    :returns boolean
    """
    # we need to return true in following cases :
    # 1. there is no last request message
    # 2. the message type is a resend request message
    if not client.last_request_message or message.command == "97":
        return True

    # get current sequence from tag AY
    sequence = message.sequence_number
    # get sequence number from last request message
    last_sequence_number = client.last_sequence_number

    return last_sequence_number and (
        int(sequence) - 1 == int(last_sequence_number)
        or (int(last_sequence_number) == 9 and int(sequence) == 0)
    )
