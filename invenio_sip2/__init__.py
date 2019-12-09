# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 UCLouvain.
#
# Invenio-SIP2 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that add SIP2 communication for self-check."""

from __future__ import absolute_import, print_function

from .ext import InvenioSIP2
from .version import __version__

__all__ = ('__version__', 'InvenioSIP2')
