#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 - S. Zachariah Sprackett <zac@sprackett.com>
#
# Released under the same terms as Sensu (the MIT license); see LICENSE
# for details.

from __future__ import print_function
from sensu_plugin.plugin import SensuPlugin


class SensuPluginCheck(SensuPlugin):
    def check_name(self, name=None):
        '''
        Return check name if defined, otherwise use the class name
        '''
        if name:
            self.plugin_info['check_name'] = name

        if self.plugin_info['check_name'] is not None:
            return self.plugin_info['check_name']

        return self.__class__.__name__

    def message(self, *m):
        '''
        Define the check message
        '''
        self.plugin_info['message'] = m

    def output(self, args):
        '''
        Print the final output message, eg.
        CheckDisk CRTITICAL: message goes here
        '''
        msg = ''
        if args is None or (args[0] is None and len(args) == 1):
            args = self.plugin_info['message']

        if args is not None and not (args[0] is None and len(args) == 1):
            msg = ": {0}".format(' '.join(str(message) for message in args))

        print("{0} {1}{2}".format(self.check_name(),
                                  self.plugin_info['status'], msg))
