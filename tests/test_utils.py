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

"""Invenio-sip1 actions test."""

from __future__ import absolute_import, print_function

from invenio_sip2.utils import convert_to_char, decode_char_to_bool, \
    ensure_i18n_language, get_language_code, parse_circulation_date


def test_decode_char_to_bool():
    """Test convert char to boolean."""
    assert decode_char_to_bool('Y')


def test_convert_char():
    """Test convert char."""
    assert convert_to_char(1) == 'Y'
    assert convert_to_char(0) == 'N'


def test_parse_circulation_date():
    """Test parse circulation date."""
    assert parse_circulation_date('2021-08-16T22:00:18.676736+00:00')
    assert parse_circulation_date('2021-08-16T22:00:18')
    assert parse_circulation_date('2021-08-16')


def test_ensure_i18n_language():
    """Test ensure i18n language."""
    assert ensure_i18n_language('en') == 'en'
    assert ensure_i18n_language('eng') == 'en'
    assert ensure_i18n_language('english') == 'en'
    assert ensure_i18n_language('fr') == 'fr'
    assert ensure_i18n_language('fra') == 'fr'
    assert ensure_i18n_language('fre') == 'fr'
    assert ensure_i18n_language('it') == 'it'
    assert ensure_i18n_language('ita') == 'it'


def test_get_language_code():
    """Test conversion of language to SIP2 code."""
    # test by ISO 639-2 language
    assert get_language_code('eng') == '001'
    # test by enum name
    assert get_language_code('FRENCH') == '002'
    # test unknown value
    assert get_language_code('inexisting_language') == '000'
