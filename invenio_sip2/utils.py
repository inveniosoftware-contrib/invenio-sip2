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

"""Invenio-SIP2 Utilities."""

from __future__ import absolute_import, print_function

import pytz
from dateutil import parser
from flask import current_app
from pycountry import languages

from .models import SelfcheckCirculationStatus, SelfcheckLanguage, \
    SelfcheckMediaType, SelfcheckSecurityMarkerType


def convert_bool_to_char(value=False):
    """Convert boolean to SIP2 char representation."""
    return 'Y' if value else 'N'


def convert_to_char(value='unknown'):
    """Convert value to SIP2 char representation."""
    if isinstance(value, str):
        return 'U'
    return 'Y' if value else 'N'


def decode_char_to_bool(value='N'):
    """Decode SIP2 char representation to boolean."""
    return value == 'Y'


def parse_circulation_date(date):
    """Converts a date of string format to a formatted date utc aware."""
    date_format = current_app.config.get('SIP2_CIRCULATION_DATE_FORMAT')
    parsed_date = parser.parse(date)
    if parsed_date.tzinfo:
        return parsed_date.strftime(date_format)
    return pytz.utc.localize(parsed_date).strftime(date_format)


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
    else:
        return language


def get_security_marker_type(marker_type=None):
    """Get mapped security marker type."""
    try:
        return getattr(SelfcheckSecurityMarkerType, marker_type)
    except AttributeError:
        return current_app.config.get('SIP2_DEFAULT_SECURITY_MARKER')


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
