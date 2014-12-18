#!/usr/bin/env python
#coding=utf-8

import sys, requests
from sensu_plugin.utils import SensuUtils

class SensuHandler(object):
    def __init__(self):
        self.settings = SensuUtils.settings()
        self.event = SensuUtils.read_event(sys.stdin.readline())
        self.handle()

    def handle(self):
        pass

    def filter(self):
        self.filter_disabled()
        self.filter_repeated()
        self.filter_silenced()

    def bail(self, msg):
        print(str(msg) + ": " + self.event['client']['name'] + "/" + self.event['check']['name'])
        sys.exit(0)

    def filter_disabled(self):
        if 'alert' in self.event['check'] and self.event['check']['alert'] == False:
            self.bail("Alert Disabled")

    def filter_repeated(self):
        occurrences = self.event['check']['occurrences'] if 'occurrences' in self.event['check'] else 1
        interval = self.event['check']['interval'] if 'interval' in self.event['check'] else 30
        refresh = self.event['check']['refresh'] if 'refresh' in self.event['check'] else 1800

        if self.event['occurrences'] < occurrences:
            self.bail("Not enough occurrences")

        if self.event['occurrences'] > occurrences and self.event['action'] == 'create':
            num = int(refresh / interval)
            if not (num == 0 or self.event['occurrences'] % num == 0):
                self.bail("Only handling every " + str(num) + " occurrences")

    def stash_exists(self, path):
        req = requests.get("http://" + self.settings['api']['host'] + ":" + self.settings['api']['port'] + path)
        if req.status_code == 200:
            return True
        return False
    
    def filter_silenced(self):
        stashes = [
            ['client', '/silence/' + self.event['client']['name']],
            ['check', '/silence/' + self.event['client']['name'] + '/' + self.event['check']['name']],
            ['check', '/silence/all/' + self.event['check']['name']]
        ]

        for scope, path in stashes:
            if self.stash_exists(path):
                self.bail(scope + " alerts silenced")
                
