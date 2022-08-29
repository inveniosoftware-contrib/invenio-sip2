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


class SelfcheckCirculationError(Exception):
    """Selfcheck Circulation error."""

    def __init__(self, error, data, **kwargs):
        """Initialize exception."""
        self.data = data
        super().__init__(error, **kwargs)


class UnknownFieldIdMessageError(Exception):
    """Unknown SIP2 field id."""

    def __init__(self, message=None, **kwargs):
        """Initialize exception."""
        self.description = f"Unknown field id message '{message}'"
        super().__init__(**kwargs)


class CommandNotFound(Exception):
    """Command not found."""

    def __init__(self, message=None, **kwargs):
        """Initialize exception."""
        self.description = message
        super().__init__(**kwargs)


# Server
class ServerMessageError(Exception):
    """Server message error."""


class ServerAlreadyRunning(Exception):
    """Server already running."""
