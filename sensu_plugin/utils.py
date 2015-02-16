#!/usr/bin/env python
# coding=utf-8

import os
import json
from sensu_plugin.conf_cache import ConfCache


class SensuUtils(object):

    @staticmethod
    def config_files():
        config_files = []
        if os.environ.get('SENSU_CONFIG_FILES'):
            config_files = os.environ.get('SENSU_CONFIG_FILES').split(':')
        else:
            config_files.append('/etc/sensu/config.json')
            for root, subdir, files in os.walk('/etc/sensu/conf.d'):
                del root
                del subdir
                for filename in files:
                    config_files.append('/etc/sensu/conf.d/' + filename)

        return config_files

    @staticmethod
    def load_config(filename):
        try:
            j_dat = open(filename)
            jobj = json.load(j_dat)
            j_dat.close()
            return jobj
        except ValueError:
            return {}
        except IOError:
            return {}

    @staticmethod
    @ConfCache
    def settings():
        settings_hash = {}
        for filename in SensuUtils.config_files():
            settings_hash.update(SensuUtils.load_config(filename))
        return settings_hash

    @staticmethod
    def read_event(json_data):
        event = {}
        try:
            event = json.loads(json_data)
        except ValueError:
            print "Error loading json"
            return {}

        if 'occurrences' not in event or not event['occurrences']:
            event['occurrences'] = 1

        for item in 'check', 'client':
            if item not in event or not event[item]:
                event[item] = {}

        return event
