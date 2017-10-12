#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 - S. Zachariah Sprackett <zac@sprackett.com>
#
# Released under the same terms as Sensu (the MIT license); see LICENSE
# for details.

from __future__ import print_function
import os
import sys
import requests
try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse
from utils import *

class SensuHandler(object):
    def __init__(self):
        # Parse the stdin into a global event object
        stdin = sys.stdin.read()
        self.read_event(stdin)

        # Prepare global settings
        self.settings = get_settings()
        self.api_settings = self.get_api_settings()

        # Filter (deprecated) and handle
        self.filter()
        self.handle()
    
    def read_event(self, check_result):
        '''
        Convert the piped check result (json) into a global 'event' dict
        '''
        try:
            self.event = json.loads(check_result)
            self.event['occurrences'] = self.event.get('occurrences', 1)
            self.event['check'] = self.event.get('check', {})
            self.event['client'] = self.event.get('client', {})
        except Exception as e:
            print('error reading event: ' + e.message)
            sys.exit(1)

    def handle(self):
        '''
        Method that should be overwritten to provide handler logic.
        '''
        print('ignoring event -- no handler defined')

    def filter(self):
        '''
        Filters exit the proccess if the event should not be handled.
        
        Filtering events is deprecated and will be removed in a future release.
        '''

        if self.deprecated_filtering_enabled():
            print('warning: event filtering in sensu-plugin is deprecated, see http://bit.ly/sensu-plugin')
            self.filter_disabled()
            self.filter_silenced()
            self.filter_dependencies()

            if self.deprecated_occurrence_filtering_enabled():
                print('warning: occurrence filtering in sensu-plugin is deprecated, see http://bit.ly/sensu-plugin')
                self.filter_repeated()

    def deprecated_filtering_enabled(self):
        '''
        Evaluates whether the event should be processed by any of the
        filter methods in this library. Defaults to true,
        i.e. deprecated filters are run by default.
        
        returns bool
        '''
        return self.event['check'].get('enable_deprecated_filtering', False)


    def deprecated_occurrence_filtering_enabled(self):
        '''
        Evaluates whether the event should be processed by the
        filter_repeated method. Defaults to true, i.e. filter_repeated
        will filter events by default.

        returns bool
        '''

        return self.event['check'].get('enable_deprecated_occurrence_filtering', False)

    def bail(self, msg):
        '''
        Gracefully terminate with message
        '''
        client_name = self.event['client'].get('name', 'error:no-client-name')
        check_name = self.event['client'].get('name', 'error:no-check-name')
        print('{}: {}/{}'.format(msg, client_name, check_name))
        sys.exit(0)

    def get_api_settings(self):
        '''
        Return a hash of API settings derived first from ENV['SENSU_API_URL'] if set,
        then Sensu config `api` scope if configured, and finally falling back to
        to ipv4 localhost address on default API port.
        
        return dict
        '''

        SENSU_API_URL = os.environ.get('SENSU_API_URL')
        if SENSU_API_URL:
            uri = urlparse(SENSU_API_URL)
            self.api_settings = {
               'host': '{0}//{1}'.format(uri.scheme,uri.hostname),
               'port': uri.port,
               'user': uri.username,
               'password': uri.password
            }
        else:
            self.api_settings = self.settings.get('api',{})
            self.api_settings['host'] = self.api_settings.get('host', '127.0.0.1')
            self.api_settings['port'] = self.api_settings.get('port', 4567)
    
    # API requests
    def api_request(method, path, blk):
        if not hasattr(self, 'api_settings'):
            ValueError('api.json settings not found')

        if method.lower() == 'get':
            _request = requests.get
        elif method.lower() == 'post':
            _request = requests.post
      
        domain = self.api_settings['host']
        # TODO: http/https
        uri = 'http://{}:{}{}'.format(domain, self.api_settings['port'], path)
        if self.api_settings['user'] and self.api_settings['password']:
            auth = (self.api_settings['user'], self.api_settings['password'])
        else:
            auth = ()
        req = _request(uri, auth=auth)
        return req
       
    def stash_exists(self, path):
        return self.api_request('get', '/stash' + path).status_code == 200

    def event_exists(self, client, check):
        return self.api_request('get', '/events/' + client + '/' + check).status_code == 200

    # Filters
    def filter_disabled(self):
        if self.event['check']['alert'] == False:
            bail('alert disabled')

    def filter_silenced(self):
        stashes = [
            ('client', '/silence/' + self.event['client']['name']),
            ('check', '/silence/' + self.event['client']['name'] + '/' + self.event['check']['name']),
            ('check', '/silence/all/' + self.event['check']['name'])
        ]
        for scope, path in stashes:
            if stash_exists(path):
                bail(scope + ' alerts silenced')
            # TODO: Timeout for querying Sensu API?
            #       More appropriate in the api_request method? 

    def filter_dependencies(self):
        dependencies = self.event['check'].get('dependencies', None)
        if dependencies == None or not isinstance(dependencies, list):
            return
        for dependency in self.event['check']['dependencies']:
            if len(str(dependency)) == 0:
                continue
            dependency_split = tuple(dependency.split('/'))
            # If there's a dependency on a check from another client, then use
            # that client name, otherwise assume same client.
            if len(dependency_split) == 2:
                client,check = dependency_split
            else:
                client = self.event['client']['name']
                check = dependency_split[0]
            if self.event_exists(client, check):
                bail('check dependency event exists')


    def filter_repeated(self):
        defaults = {
            'occurrences': 1,
            'interval': 30,
            'refresh': 1800
        }

        # Override defaults with anything defined in the settings 
        if isinstance(self.settings['sensu_plugin'], dict):
            defaults.update(settings['sensu_plugin'])
        end

        occurrences = int(self.event['check'].get('occurrences', defaults['occurrences']))
        interval = int(self.event['check'].get('interval', defaults['interval']))
        refresh = int(self.event['check'].get('refresh', defaults['refresh']))

        if self.event['occurrences'] < occurrences:
            bail('not enough occurrences')
      
        if self.event['occurrences'] > occurrences and self.event['action'] == 'create':
            return
        
        number = int(refresh / interval)
        if (number == 0) or ((self.event['occurrences'] - occurrences) % number == 0):
            return

        bail('only handling every ' + str(number) + ' occurrences')
