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

from werkzeug.local import LocalProxy

from invenio_sip2.ext import InvenioSIP2
from invenio_sip2.proxies import current_datastore, current_sip2
from invenio_sip2.version import __version__

datastore = LocalProxy(lambda: current_sip2.datastore)

__all__ = (
    '__version__',
    'current_datastore',
    'current_sip2',
    'InvenioSIP2'
)
