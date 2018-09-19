#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 - S. Zachariah Sprackett <zac@sprackett.com>
#
# Released under the same terms as Sensu (the MIT license); see LICENSE
# for details.

'''
This provides a base SensuHandler class that can be used for writing
python-based Sensu handlers.
'''

from __future__ import print_function
import argparse
import os
import sys
import json
import requests
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
from sensu_plugin.utils import get_settings, map_v2_event_into_v1


class SensuHandler(object):
    '''
    Base class for Sensu Handlers.
    '''

    def __init__(self, autorun=True):

        if autorun:
            self.run()

    def run(self):
        '''
        Set up the event object, global settings and command line
        arguments.
        '''

        # Parse the stdin into a global event object
        stdin = self.read_stdin()
        self.event = self.read_event(stdin)

        # Prepare global settings
        self.settings = get_settings()
        self.api_settings = self.get_api_settings()

        # Prepare command line arguments and
        self.parser = argparse.ArgumentParser()

        # set up the 2.x to 1.x event mapping argument
        self.parser.add_argument("--map-v2-event-into-v1",
                                 action="store_true",
                                 default=False,
                                 dest="v2event")

        if hasattr(self, 'setup'):
            self.setup()
        (self.options, self.remain) = self.parser.parse_known_args()

        # map the event if required
        if (self.options.v2event or
                os.environ.get("SENSU_MAP_V2_EVENT_INTO_V1")):
            self.event = map_v2_event_into_v1(self.event)

        # Filter (deprecated) and handle
        self.filter()
        self.handle()

    def read_stdin(self):
        '''
        Read data piped from stdin.
        '''
        try:
            return sys.stdin.read()
        except Exception:
            raise ValueError('Nothing read from stdin')

    def read_event(self, check_result):
        '''
        Convert the piped check result (json) into a global 'event' dict
        '''
        try:
            event = json.loads(check_result)
            event['occurrences'] = event.get('occurrences', 1)
            event['check'] = event.get('check', {})
            event['client'] = event.get('client', {})
            return event
        except Exception:
            raise ValueError('error reading event: ' + check_result)

    def handle(self):
        '''
        Method that should be overwritten to provide handler logic.
        '''
        print("ignoring event -- no handler defined.")

    def filter(self):
        '''
        Filters exit the proccess if the event should not be handled.
        Filtering events is deprecated and will be removed in a future release.
        '''

        if self.deprecated_filtering_enabled():
            print('warning: event filtering in sensu-plugin is deprecated,' +
                  'see http://bit.ly/sensu-plugin')
            self.filter_disabled()
            self.filter_silenced()
            self.filter_dependencies()

            if self.deprecated_occurrence_filtering():
                print('warning: occurrence filtering in sensu-plugin is' +
                      'deprecated, see http://bit.ly/sensu-plugin')
                self.filter_repeated()

    def deprecated_filtering_enabled(self):
        '''
        Evaluates whether the event should be processed by any of the
        filter methods in this library. Defaults to true,
        i.e. deprecated filters are run by default.

        returns bool
        '''
        return self.event['check'].get('enable_deprecated_filtering', False)

    def deprecated_occurrence_filtering(self):
        '''
        Evaluates whether the event should be processed by the
        filter_repeated method. Defaults to true, i.e. filter_repeated
        will filter events by default.

        returns bool
        '''

        return self.event['check'].get(
            'enable_deprecated_occurrence_filtering', False)

    def bail(self, msg):
        '''
        Gracefully terminate with message
        '''
        client_name = self.event['client'].get('name', 'error:no-client-name')
        check_name = self.event['check'].get('name', 'error:no-check-name')
        print('{}: {}/{}'.format(msg, client_name, check_name))
        sys.exit(0)

    def get_api_settings(self):
        '''
        Return a dict of API settings derived first from ENV['SENSU_API_URL']
        if set, then Sensu config `api` scope if configured, and finally
        falling back to to ipv4 localhost address on default API port.

        return dict
        '''

        sensu_api_url = os.environ.get('SENSU_API_URL')
        if sensu_api_url:
            uri = urlparse(sensu_api_url)
            api_settings = {
                'host': '{0}://{1}'.format(uri.scheme, uri.hostname),
                'port': uri.port,
                'user': uri.username,
                'password': uri.password
            }
        else:
            api_settings = self.settings.get('api', {})
            api_settings['host'] = api_settings.get(
                'host', '127.0.0.1')
            api_settings['port'] = api_settings.get(
                'port', 4567)

        return api_settings

    # API requests
    def api_request(self, method, path):
        '''
        Query Sensu api for information.
        '''
        if not hasattr(self, 'api_settings'):
            ValueError('api.json settings not found')

        if method.lower() == 'get':
            _request = requests.get
        elif method.lower() == 'post':
            _request = requests.post

        domain = self.api_settings['host']
        uri = '{}:{}/{}'.format(domain, self.api_settings['port'], path)
        if self.api_settings.get('user') and self.api_settings.get('password'):
            auth = (self.api_settings['user'], self.api_settings['password'])
        else:
            auth = ()
        req = _request(uri, auth=auth)
        return req

    def stash_exists(self, path):
        '''
        Query Sensu API for stash data.
        '''
        return self.api_request('get', '/stash' + path).status_code == 200

    def event_exists(self, client, check):
        '''
        Query Sensu API for event.
        '''
        return self.api_request(
            'get',
            'events/{}/{}'.format(client, check)
            ).status_code == 200

    # Filters
    def filter_disabled(self):
        '''
        Determine whether a check is disabled and shouldn't handle.
        '''
        if self.event['check']['alert'] is False:
            self.bail('alert disabled')

    def filter_silenced(self):
        '''
        Determine whether a check is silenced and shouldn't handle.
        '''
        stashes = [
            ('client', '/silence/{}'.format(self.event['client']['name'])),
            ('check', '/silence/{}/{}'.format(
                self.event['client']['name'],
                self.event['check']['name'])),
            ('check', '/silence/all/{}'.format(self.event['check']['name']))
        ]
        for scope, path in stashes:
            if self.stash_exists(path):
                self.bail(scope + ' alerts silenced')

    def filter_dependencies(self):
        '''
        Determine whether a check has dependencies.
        '''
        dependencies = self.event['check'].get('dependencies', None)
        if dependencies is None or not isinstance(dependencies, list):
            return
        for dependency in self.event['check']['dependencies']:
            if not str(dependency):
                continue
            dependency_split = tuple(dependency.split('/'))
            # If there's a dependency on a check from another client, then use
            # that client name, otherwise assume same client.
            if len(dependency_split) == 2:
                client, check = dependency_split
            else:
                client = self.event['client']['name']
                check = dependency_split[0]
            if self.event_exists(client, check):
                self.bail('check dependency event exists')

    def filter_repeated(self):
        '''
        Determine whether a check is repeating.
        '''
        defaults = {
            'occurrences': 1,
            'interval': 30,
            'refresh': 1800
        }

        # Override defaults with anything defined in the settings
        if isinstance(self.settings['sensu_plugin'], dict):
            defaults.update(self.settings['sensu_plugin'])

        occurrences = int(self.event['check'].get(
            'occurrences', defaults['occurrences']))
        interval = int(self.event['check'].get(
            'interval', defaults['interval']))
        refresh = int(self.event['check'].get(
            'refresh', defaults['refresh']))

        if self.event['occurrences'] < occurrences:
            self.bail('not enough occurrences')

        if (self.event['occurrences'] > occurrences and
                self.event['action'] == 'create'):
            return

        number = int(refresh / interval)
        if (number == 0 or
                (self.event['occurrences'] - occurrences) % number == 0):
            return

        self.bail('only handling every ' + str(number) + ' occurrences')
