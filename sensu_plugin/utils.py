#!/usr/bin/env python

import os
import json
from memo import memoize

class SensuUtils(object):

    @staticmethod
    def config_files():
        config_files = []
        if os.environ.get('SENSU_CONFIG_FILES'):
            config_files = os.environ.get('SENSU_CONFIG_FILES').split(':')
        else:
            config_files.append('/etc/sensu/config.json')
            for root, subdir, files in os.walk('/etc/sensu/conf.d'):
                for f in files:
                    config_files.append('/etc/sensu/conf.d/' + f)
    
        return config_files
    

    @staticmethod
    def load_config(filename):
        try:
            j_dat = open(filename)
            jobj = json.load(j_dat)
            j_dat.close()
            return jobj
        except:
            return {}

    @staticmethod
    @memoize
    def settings():
        settings_hash = {}
        for f in SensuUtils.config_files():
            settings_hash.update(SensuUtils.load_config(f))
        return settings_hash

    @staticmethod
    def read_event(json_data):
        event = {}
        try:
            event = json.loads(json_data)
            if not 'occurrences' in event or not event['occurrences']:
                event['occurrences'] = 1

            for x in 'check', 'client':
                if not x in event or not event[x]:
                    event[x] = {}
        except Exception as e:
            print "Error reading event: " + e.message

        return event
                



 
