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

"""Blueprint for Invenio-SIP2."""

from flask import Blueprint, render_template
from flask_babelex import gettext as _

from invenio_sip2.records import Server

blueprint = Blueprint(
    'invenio_sip2',
    __name__,
    template_folder='../templates',
    static_folder='../static',
)


@blueprint.route("/sip2/monitoring")
def monitoring():
    """Render a basic view."""
    return render_template(
        "invenio_sip2/monitoring.html",
        module_name=_('Invenio-SIP2'),
        servers=list(Server.get_all_records()))
