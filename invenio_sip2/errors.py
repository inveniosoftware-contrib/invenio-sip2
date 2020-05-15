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

"""Invenio-SIP2 exceptions."""


# Actions
class InvalidSelfCheckActionError(Exception):
    """Action not found in sip2 configuration."""

    def __init__(self, action=None, **kwargs):
        """Initialize exception."""
        self.description = "Invalid selfcheck '{}'".format(action)
        super().__init__(**kwargs)


class SelfCheckActionError(Exception):
    """Action error in sip2."""

    def __init__(self, action=None, **kwargs):
        """Initialize exception."""
        self.description = "selfcheck action error'{}'".format(action)
        super().__init__(**kwargs)


# Message
class InvalidSelfCheckMessageError(Exception):
    """Invalid SIP2 message."""

    def __init__(self, message=None, **kwargs):
        """Initialize exception."""
        self.description = "Invalid selfcheck message '{}'".format(message)
        super().__init__(**kwargs)


class UnknownFieldIdMessageError(Exception):
    """Unknown SIP2 field id."""

    def __init__(self, message=None, **kwargs):
        """Initialize exception."""
        self.description = "Unknown field id message '{}'".format(message)
        super().__init__(**kwargs)
