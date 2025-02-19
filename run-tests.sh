#!/usr/bin/env bash
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

function tests () {
  set -e
  info_msg "Test pydocstyle:"
  pydocstyle invenio_sip2 tests docs

  info_msg "Test isort:"
  isort invenio_sip2 tests --check-only --diff

  info_msg "Test useless imports:"
  autoflake --recursive --remove-all-unused-imports --ignore-init-module-imports --check-diff --quiet .

  info_msg "Sphinx-build:"
  sphinx-build -qnNW docs docs/_build/html

  info_msg "Tests:"
  poetry run pytest
}

if [ $# -eq 0 ]
  then
    tests
    exit "$?"
fi

if [ "$1" = "docker-services" ]
  then
    docker-services-cli up --db ${DB:-postgresql} --cache ${CACHE:-redis} --mq ${MQ:-redis} --env
    tests
    tests_exit_code=$?
    docker-services-cli down
    exit "$tests_exit_code"
fi
