# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 UCLouvain.
#
# Invenio-SIP2 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

from flask import Flask
from invenio_sip2 import InvenioSIP2


def test_version():
    """Test version import."""
    from invenio_sip2 import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = InvenioSIP2(app)
    assert 'invenio-sip2' in app.extensions

    app = Flask('testapp')
    ext = InvenioSIP2()
    assert 'invenio-sip2' not in app.extensions
    ext.init_app(app)
    assert 'invenio-sip2' in app.extensions


def test_view(base_client):
    """Test view."""
    res = base_client.get("/")
    assert res.status_code == 200
    assert 'Welcome to Invenio-SIP2' in str(res.data)
