#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import atexit
import os
import sys
import traceback

from collections import namedtuple

from sensu_plugin.exithook import ExitHook

# create a namedtuple of all valid exit codes
ExitCode = namedtuple('ExitCode', ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN'])


class SensuPlugin(object):
    '''
    Base class used by both checks and metrics plugins.
    '''
    def __init__(self, autorun=True):

        self.plugin_info = {
            'check_name': None,
            'message': None,
            'status': None
        }

        # create a method for each of the exit codes
        # and register as exiy functions
        self._hook = ExitHook()
        self._hook.hook()

        self.exit_code = ExitCode(0, 1, 2, 3)
        for field in self.exit_code._fields:
            self.__make_dynamic(field)

        atexit.register(self.__exitfunction)

        # Prepare command line arguments
        self.parser = argparse.ArgumentParser()
        if hasattr(self, 'setup'):
            self.setup()
        (self.options, self.remain) = self.parser.parse_known_args()

        if autorun:
            self.run()

    def output(self, args):
        '''
        Print the output message.
        '''
        print("SensuPlugin: {}".format(' '.join(str(a) for a in args)))

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
        Method should be overwritten by inherited classes.
        '''
        self.warning("Not implemented! You should override SensuPlugin.run()")

    def __exitfunction(self):
        '''
        Method called by exit hook, ensures that both an exit code and
        output is supplied, also catches errors.
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
