#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 - S. Zachariah Sprackett <zac@sprackett.com>
#
# Released under the same terms as Sensu (the MIT license); see LICENSE
# for details.

from __future__ import print_function
import atexit
import sys
import argparse
import os
import traceback
from collections import namedtuple
from sensu_plugin.exithook import ExitHook

ExitCode = namedtuple('ExitCode', ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN'])


class SensuPlugin(object):
    def __init__(self):
        self.plugin_info = {
            'check_name': None,
            'message': None,
            'status': None
        }

        # TODO: Split this futher into its own method and call in __init__?

        self._hook = ExitHook()
        self._hook.hook() # TODO: What does this do??

        self.exit_code = ExitCode(0, 1, 2, 3)
        for field in self.exit_code._fields:
            self.__make_dynamic(field)
            # TODO: What does this ACHIEVE? self.ok, etc. but WHY?

        atexit.register(self.__exitfunction)

        # self.setup is defined in inherited classes to set up CLI args using
        # self.parser. arguments are then saved as methods of self.options
        self.parser = argparse.ArgumentParser()
        if hasattr(self, 'setup'):
            self.setup()

        self.parse_args()

    def output(self, args):
        print("SensuPlugin: %s" % ' '.join(str(a) for a in args))

    def parse_args(self):
        '''
        Return a tuple containing arguments (and their values) specified to argparse and any extras.
        '''
        return (self.options, self.remain) = self.parser.parse_known_args()

    def __make_dynamic(self, method):
        '''
        Create a method for each of the exit codes.
        '''

        def dynamic(*args):
            self.plugin_info['status'] = method
            if not args:
                args = None
            self.output(args)
            sys.exit(getattr(self.exit_code, method))

        method_lc = method.lower()
        dynamic.__doc__ = "%s method" % method_lc
        dynamic.__name__ = method_lc
        setattr(self, dynamic.__name__, dynamic)

    def run(self):
        '''
        Method to be overwritten by inherited classes.
        '''
        self.warning("Not implemented! You should override SensuPlugin.run()")

    def __exitfunction(self):
        '''
        Method called by exit hook.
        Will ensure that an exit code and output is supplied and also catch
        errors.
        '''
        if self._hook.exit_code is None and self._hook.exception is None:
            print("Check did not exit! You should call an exit code method.")
            sys.stdout.flush()
            os._exit(1)
        elif self._hook.exception:
            print("Check failed to run: %s, %s" %
                  (sys.last_type, traceback.format_tb(sys.last_traceback)))
            sys.stdout.flush()
            os._exit(2)
