#!/usr/bin/env sh
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

RED='\033[0;31m'
GREEN='\033[0;0;32m'
NC='\033[0m' # No Color

display_error_message () {
	echo -e "${RED}$1${NC}" 1>&2
}

display_success_message () {
    echo -e "${GREEN}$1${NC}" 1>&2
}

display_error_message_and_exit () {
  display_error_message "$1"
  exit 1
}

if [ $# -eq 0 ]
    then
        set -e
        # pipenv check -i 36759
        display_success_message "Test pydocstyle:"
        pydocstyle invenio_sip2 tests docs
        display_success_message "Test isort:"
        isort -rc -c -df
        echo -e ${GREEN}Test useless imports:${NC}
        autoflake --remove-all-unused-imports -c -r --ignore-init-module-imports . || display_error_message_and_exit "\nUse this command to check imports:\n\tautoflake --remove-all-unused-imports -r --ignore-init-module-imports .\n"
        display_success_message "Check-manifest:"
        check-manifest --ignore ".travis-*,docs/_build*"
        display_success_message "Sphinx-build:"
        sphinx-build -qnNW docs docs/_build/html
        display_success_message "Tests:"
        python setup.py test
fi
