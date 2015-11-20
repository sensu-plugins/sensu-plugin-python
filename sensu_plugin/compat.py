#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=undefined-variable
"""
Python 2/3 compatibility code.
"""

try:
    compat_basestring = basestring
except NameError:  # Python 3
    compat_basestring = (bytes, str)
