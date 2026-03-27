#!/usr/bin/env bash
# INVENIO-SIP2
# Copyright (C) 2020-2026 UCLouvain, RERO+
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

# COLORS for messages
NC='\033[0m'                    # Default color
INFO_COLOR='\033[1;97;44m'      # Bold + white + blue background
SUCCESS_COLOR='\033[1;97;42m'   # Bold + white + green background
ERROR_COLOR='\033[1;97;41m'     # Bold + white + red background

SCRIPT_PATH=$(dirname "$0")

PROGRAM=`basename $0`
SCRIPT_PATH=$(dirname "$0")

# MESSAGES
msg() {
  echo -e "${1}" 1>&2
}
# Display a colored message
# More info: https://misc.flogisoft.com/bash/tip_colors_and_formatting
# $1: choosen color
# $2: title
# $3: the message
colored_msg() {
  msg "${1}[${2}]: ${3}${NC}"
}

info_msg() {
  colored_msg "${INFO_COLOR}" "INFO" "${1}"
}

error_msg() {
  colored_msg "${ERROR_COLOR}" "ERROR" "${1}"
}

error_msg+exit() {
  error_msg "${1}" && exit 1
}

success_msg() {
  colored_msg "${SUCCESS_COLOR}" "SUCCESS" "${1}"
}

success_msg+exit() {
  colored_msg "${SUCCESS_COLOR}" "SUCCESS" "${1}" && exit 0
}

# Displays program name
msg "PROGRAM: ${PROGRAM}"

pip_audit_exceptions=""
add_exceptions() {
  pip_audit_exceptions="$pip_audit_exceptions --ignore-vuln $1"
}
# pytest       8.4.2   CVE-2025-71176 9.0.3
add_exceptions "CVE-2025-71176"

function tests () {
  set -e
  info_msg "Check vulnerabilities:"

  pip-audit ${pip_audit_exceptions}

  info_msg "Ruff check:"
  ruff check

  info_msg "Ruff format check:"
  ruff format --check

  info_msg "Tests:"
  pytest
}

docker-services-cli up --db ${DB:-postgresql} --cache ${CACHE:-redis} --mq ${MQ:-redis} --env
tests
tests_exit_code=$?
docker-services-cli down
exit "$tests_exit_code"
