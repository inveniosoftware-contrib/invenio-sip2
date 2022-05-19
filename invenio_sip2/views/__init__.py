# -*- coding: utf-8 -*-
#
# INVENIO-SIP2
# Copyright (C) 2021 UCLouvain
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

"""Blueprints for invenio-sip2."""

from invenio_sip2.views.rest import api_blueprint
from invenio_sip2.views.views import blueprint

__all__ = (
    'blueprint',
    'api_blueprint',
)
