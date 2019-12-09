#!/usr/bin/env sh
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 UCLouvain.
#
# Invenio-SIP2 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
        pipenv check -i 36759
        display_success_message "Test pydocstyle:"
        pipenv run pydocstyle invenio_sip2 tests docs
        display_success_message "Test isort:"
        pipenv run isort -rc -c -df
        echo -e ${GREEN}Test useless imports:${NC}
        pipenv run autoflake --remove-all-unused-imports -c -r --ignore-init-module-imports . || display_error_message_and_exit "\nUse this command to check imports:\n\tautoflake --remove-all-unused-imports -r --exclude ui --ignore-init-module-imports .\n"
        display_success_message "Check-manifest:"
        pipenv run check-manifest --ignore ".travis-*,docs/_build*"
        display_success_message "Sphinx-build:"
        pipenv run sphinx-build -qnNW docs docs/_build/html
        display_success_message "Tests:"
        pipenv run test
fi
