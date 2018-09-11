#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from sensu_plugin.plugin import SensuPlugin


class SensuPluginCheck(SensuPlugin):
    '''
    Class that inherits from SensuPlugin.
    '''
    def check_name(self, name=None):
        '''
        Checks the plugin name and sets it accordingly.
        Uses name if specified, class name if not set.
        '''
        if name:
            self.plugin_info['check_name'] = name

        if self.plugin_info['check_name'] is not None:
            return self.plugin_info['check_name']

        return self.__class__.__name__

    def message(self, *m):
        self.plugin_info['message'] = m

    def output(self, args):
        msg = ''
        if args is None or (args[0] is None and len(args) == 1):
            args = self.plugin_info['message']

        if args is not None and not (args[0] is None and len(args) == 1):
            msg = ": {0}".format(' '.join(str(message) for message in args))

        print("{0} {1}{2}".format(self.check_name(),
                                  self.plugin_info['status'], msg))
