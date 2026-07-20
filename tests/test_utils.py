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

"""Invenio-sip1 actions test."""

from invenio_sip2.utils import (
    convert_to_char,
    decode_char_to_bool,
    ensure_i18n_language,
    get_language_code,
    mask_sensitive_data,
    parse_circulation_date,
    verify_checksum,
)


def test_decode_char_to_bool():
    """Test convert char to boolean."""
    assert decode_char_to_bool("Y")


def test_convert_char():
    """Test convert char."""
    assert convert_to_char(1) == "Y"
    assert convert_to_char(0) == "N"


def test_parse_circulation_date():
    """Test parse circulation date."""
    assert parse_circulation_date("2021-08-16T22:00:18.676736+00:00")
    assert parse_circulation_date("2021-08-16T22:00:18")
    assert parse_circulation_date("2021-08-16")


def test_ensure_i18n_language():
    """Test ensure i18n language."""
    assert ensure_i18n_language("en") == "en"
    assert ensure_i18n_language("eng") == "en"
    assert ensure_i18n_language("english") == "en"
    assert ensure_i18n_language("fr") == "fr"
    assert ensure_i18n_language("fra") == "fr"
    assert ensure_i18n_language("fre") == "fr"
    assert ensure_i18n_language("it") == "it"
    assert ensure_i18n_language("ita") == "it"


def test_get_language_code():
    """Test conversion of language to SIP2 code."""
    # test by ISO 639-2 language
    assert get_language_code("eng") == "001"
    # test by enum name
    assert get_language_code("FRENCH") == "002"
    # test unknown value
    assert get_language_code("inexisting_language") == "000"


def test_verify_checksum(app):
    """Test checksum verification for byte-summing and code-point clients."""
    # SIP2 message body up to the "AZ" checksum identifier. It contains non-ASCII
    # characters ("€", "é") whose UTF-8 byte sum differs from their code point, so
    # byte-summing and code-point-summing clients build a different checksum for
    # the very same message.
    body = "6300120260720    051335          AO|AA123456|AC|AD$kajshkj#€ééé|AY3AZ"

    def checksum(total):
        return format(-total & 0xFFFF, "04X")

    byte_checksum = checksum(sum(body.encode("UTF-8")))
    codepoint_checksum = checksum(sum(ord(char) for char in body))
    # the two interpretations genuinely diverge because of the non-ASCII chars
    assert byte_checksum != codepoint_checksum

    # both interpretations are accepted
    assert verify_checksum(f"{body}{byte_checksum}")
    assert verify_checksum(f"{body}{codepoint_checksum}")
    # a corrupted checksum is still rejected
    assert not verify_checksum(f"{body}0000")


def test_mask_sensitive_data():
    """Test masking of credential fields in raw SIP2 messages."""
    # patron information request: patron password (AD) is masked
    request = "6300120260720    051335          AO|AA123456|AC|AD$ecretPwd|AY3AZCC19"
    masked = mask_sensitive_data(request)
    assert "$ecretPwd" not in masked
    assert "AD****" in masked
    # non-sensitive fields (e.g. patron id) are left untouched
    assert "AA123456" in masked
    # empty credential field has no value to mask
    assert "|AC|" in masked

    # login request: login password (CO) is masked
    login = "9300CNsip2ebook1|COs3cret|AY1AZF435"
    masked_login = mask_sensitive_data(login)
    assert "s3cret" not in masked_login
    assert "CO****" in masked_login

    # message without variable fields is returned unchanged
    assert mask_sensitive_data("9900402.00AY2AZFCA3") == "9900402.00AY2AZFCA3"
