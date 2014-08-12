#!/usr/bin/env python
#coding=utf-8

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
import json
import traceback
from collections import namedtuple
from sensu_plugin.exithook import ExitHook

ExitCode = namedtuple('ExitCode', ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN'])


class SensuPlugin(object):
    def __init__(self):
        self.settings = {}
        self.config_files = []
        self.get_settings()
        self.plugin_info = {
            'check_name': None,
            'message': None,
            'status': None
        }
        self._hook = ExitHook()
        self._hook.hook()
        self.exit_code = ExitCode(0, 1, 2, 3)
        for field in self.exit_code._fields:
            self.__make_dynamic(field)
        atexit.register(self.__exitfunction)

        self.parser = argparse.ArgumentParser()
        if hasattr(self, 'setup'):
            self.setup()
        (self.options, self.remain) = self.parser.parse_known_args()

        self.run()

    def get_json(self, file_handler):
        all_data = json.load(file_handler)
        for key in all_data.iteritems():
            self.settings[key[0]] = key[1]

    def get_settings(self):
        if 'SENSU_CONFIG_FILE' in os.environ:
            env_var = os.environ['SENSU_CONFIG_FILE']
            self.config_files.append(env_var)

        else:
            self.config_files.append('/etc/sensu/config.json')
            self.config_files.append('/etc/sensu/conf.d/')

        for config_file in self.config_files:
            if os.path.isfile(config_file):
                with open(config_file) as f_handler:
                    self.get_json(f_handler)
            elif os.path.isdir(config_file):
                for _, _, files in os.walk(config_file):
                    for f_file in files:
                        f_path = config_file+f_file
                        if f_path.endswith('.json'):
                            with open(f_path) as f_handler:
                                self.get_json(f_handler)

    def output(self, args):
        print("SensuPlugin: %s" % ' '.join(str(a) for a in args))

    def __make_dynamic(self, method):

        def dynamic(*args):
            self.plugin_info['status'] = method
            if len(args) == 0:
                args = None
            self.output(args)
            sys.exit(getattr(self.exit_code, method))

        method_lc = method.lower()
        dynamic.__doc__ = "%s method" % method_lc
        dynamic.__name__ = method_lc
        setattr(self, dynamic.__name__, dynamic)

    def run(self):
        self.warning("Not implemented! You should override SensuPlugin.run()")

    def __exitfunction(self):
        if self._hook.exit_code is None and self._hook.exception is None:
            print("Check did not exit! You should call an exit code method.")
            sys.stdout.flush()
            os._exit(1)
        elif self._hook.exception:
            print("Check failed to run: %s, %s" %
                  (sys.last_type, traceback.format_tb(sys.last_traceback)))
            sys.stdout.flush()
            os._exit(2)
