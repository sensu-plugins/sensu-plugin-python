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


class SensuPluginMetricGeneric(SensuPlugin):
    def sanitise_arguments(self, args):
        # check whether the arguments have been passed by a dynamic status code
        # or if the output method is being called directly
        # extract the required tuple if called using dynamic function
        if len(args) == 1 and isinstance(args[0], tuple):
            args = args[0]
        # check to see whether output is running after being called by an empty
        # dynamic function.
        if args[0] is None:
            pass
        # check to see whether output is running after being called by a
        # dynamic whilst containing a message.
        elif isinstance(args[0], Exception) or len(args) == 1:
            print(args[0])
        else:
            return args


class SensuPluginMetricGraphite(SensuPluginMetricGeneric):
    def output(self, *args):
        # sanitise the arguments
        args = self.sanitise_arguments(args)
        if args:
            # convert the arguments to a list
            args = list(args)
            # add the timestamp if required
            if len(args) < 3:
                args.append(None)
            if args[2] is None:
                args[2] = (int(time.time()))
            # produce the output
            print(" ".join(str(s) for s in args[0:3]))


class SensuPluginMetricInfluxdb(SensuPluginMetricGeneric):
    def output(self, *args):
        # sanitise the arguments
        args = self.sanitise_arguments(args)
        if args:
            # determine whether a single value has been passed
            # as fields and if so give it a name.
            fields = args[1]
            if fields.isnumeric():
                fields = "value={}".format(args[1])
            # append tags on to the measurement name if they exist
            measurement = args[0]
            if len(args) > 2:
                measurement = "{},{}".format(args[0], args[2])
            # create a timestamp
            timestamp = int(time.time())
            # produce the output
            print("{} {} {}".format(measurement, fields, timestamp))


class SensuPluginMetricJSON(SensuPluginMetricGeneric):
    def output(self, args):
        obj = args[0]
        if isinstance(obj, (Exception, compat_basestring)):
            print(obj[0])
        elif isinstance(obj, (dict, list)):
            print(json.dumps(obj))


class SensuPluginMetricStatsd(SensuPluginMetricGeneric):
    def output(self, *args):
        # sanitise the arguments
        args = self.sanitise_arguments(args)
        if args:
            # convert the arguments to a list
            args = list(args)
            if len(args) < 3 or args[2] is None:
                stype = 'kv'
            else:
                stype = args[2]
            # produce the output
            print("|".join([":".join(str(s) for s in args[0:2]), stype]))
