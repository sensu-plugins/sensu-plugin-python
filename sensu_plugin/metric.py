#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 - S. Zachariah Sprackett <zac@sprackett.com>
#
# Released under the same terms as Sensu (the MIT license); see LICENSE
# for details.

from __future__ import print_function
import json
import time
from sensu_plugin.plugin import SensuPlugin
from sensu_plugin.compat import compat_basestring


class SensuPluginMetricJSON(SensuPlugin):
    def output(self, args):
        obj = args[0]
        if isinstance(obj, (Exception, compat_basestring)):
            print(obj)
        elif isinstance(obj, (dict, list)):
            print(json.dumps(obj))


class SensuPluginMetricGraphite(SensuPlugin):
    def output(self, *args):
        if args[0] is None:
            print()
        elif isinstance(args[0], Exception) or args[1] is None:
            print(args[0])
        else:
            l_args = list(args)
            if len(l_args) < 3:
                l_args.append(None)
            if l_args[2] is None:
                l_args[2] = int(time.time())
            print("\t".join(str(s) for s in l_args[0:3]))


class SensuPluginMetricStatsd(SensuPlugin):
    def output(self, *args):
        if args[0] is None:
            print()
        elif isinstance(args[0], Exception) or args[1] is None:
            print(args[0])
        else:
            l_args = list(args)
            if len(l_args) < 3 or l_args[2] is None:
                stype = 'kv'
            else:
                stype = l_args[2]
            print("|".join([":".join(str(s) for s in l_args[0:2]), stype]))
