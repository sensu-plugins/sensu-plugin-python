#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys


class ExitHook(object):
    def __init__(self):
        self._orig_exit = None
        self.exit_code = None
        self.exception = None

    def hook(self):
        self._orig_exit = sys.exit
        sys.exit = self.exit
        sys.excepthook = self.exc_handler

    def exit(self, code=0):
        self.exit_code = code
        self._orig_exit(code)

    def exc_handler(self, _exc_type, exc, *_args):
        self.exception = exc
