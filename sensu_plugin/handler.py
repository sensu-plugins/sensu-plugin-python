#!/usr/bin/env python
#coding=utf-8

import sys, requests
from sensu_plugin.utils import SensuUtils

class SensuHandler(object):
    def __init__(self):
        self.settings = SensuUtils.settings()
        self.event = SensuUtils.read_event(sys.stdin.readline())
        self.filter()
        self.handle()

    def handle(self):
        pass

    def filter(self):
        self.filter_disabled()
        self.filter_repeated()
        self.filter_silenced()

    def bail(self, msg):
        client_name = self.event['client']['name']
        check_name = self.event['check']['name']
        print str(msg)+ ": "+client_name+"/"+check_name
        sys.exit(0)

    def filter_disabled(self):
        if self.event['check'].get('alert', True) == False:
            self.bail("Alert Disabled")

    def filter_repeated(self):
        ocr = self.event['check'].get('occurrences', 1)
        interval = self.event['check'].get('interval', 30)
        refresh = self.event['check'].get('refresh', 1800)

        if self.event['occurrences'] < ocr:
            self.bail("Not enough occurrences")

        if self.event['occurrences'] > ocr and self.event['action'] == 'create':
            num = int(refresh / interval)
            if not (num == 0 or self.event['occurrences'] % num == 0):
                self.bail("Only handling every " + str(num) + " occurrences")

    def stash_exists(self, path):
        api_host = self.settings['api']['host']
        api_port = self.settings['api']['port']
        req = requests.get(
            "http://"+api_host+":"+api_port+path)
        if req.status_code == 200:
            return True
        return False

    def filter_silenced(self):
        client_name = self.event['client']['name']
        check_name = self.event['check']['name']
        stashes = [
            ['client', '/silence/' + client_name],
            ['check', '/silence/' + client_name + '/' + check_name],
            ['check', '/silence/all/' + check_name]
        ]

        for scope, path in stashes:
            if self.stash_exists(path):
                self.bail(scope + " alerts silenced")

