'''
Utilities for loading config files, etc.
'''

import os
import json

from copy import deepcopy


def config_files():
    '''
    Get list of currently used config files.
    '''
    sensu_loaded_tempfile = os.environ.get('SENSU_LOADED_TEMPFILE')
    sensu_config_files = os.environ.get('SENSU_CONFIG_FILES')
    sensu_v1_config = '/etc/sensu/config.json'
    sensu_v1_confd = '/etc/sensu/conf.d'
    if sensu_loaded_tempfile and os.path.isfile(sensu_loaded_tempfile):
        with open(sensu_loaded_tempfile, 'r') as tempfile:
            contents = tempfile.read()
            return contents.split(':')
    elif sensu_config_files:
        return sensu_config_files.split(':')
    else:
        files = []
        filenames = []
        if os.path.isfile(sensu_v1_config):
            files = [sensu_v1_config]
        if os.path.isdir(sensu_v1_confd):
            filenames = [f for f in os.listdir(sensu_v1_confd)
                         if os.path.splitext(f)[1] == '.json']
            for filename in filenames:
                files.append('{}/{}'.format(sensu_v1_confd, filename))
        return files


def get_settings():
    '''
    Get all currently loaded settings.
    '''
    settings = {}
    for config_file in config_files():
        config_contents = load_config(config_file)
        if config_contents is not None:
            settings = deep_merge(settings, config_contents)
    return settings


def load_config(filename):
    '''
    Read contents of config file.
    '''
    try:
        with open(filename, 'r') as config_file:
            return json.loads(config_file.read())
    except IOError:
        pass


def deep_merge(dict_one, dict_two):
    '''
    Deep merge two dicts.
    '''
    merged = dict_one.copy()
    for key, value in dict_two.items():
        # value is equivalent to dict_two[key]
        if (key in dict_one and
                isinstance(dict_one[key], dict) and
                isinstance(value, dict)):
            merged[key] = deep_merge(dict_one[key], value)
        elif (key in dict_one and
              isinstance(dict_one[key], list) and
              isinstance(value, list)):
            merged[key] = list(set(dict_one[key] + value))
        else:
            merged[key] = value
    return merged


def map_v2_event_into_v1(event):
    '''
    Helper method to convert Sensu 2.x event into Sensu 1.x event.
    '''

    # return the event if it has already been mapped
    if "v2_event_mapped_into_v1" in event:
        return event

    # Trigger mapping code if enity exists and client does not
    if not bool(event.get('client')) and "entity" in event:
        event['client'] = event['entity']

        # Fill in missing client attributes
        if "name" not in event['client']:
            event['client']['name'] = event['entity']['id']

        if "subscribers" not in event['client']:
            event['client']['subscribers'] = event['entity']['subscriptions']

        # Fill in renamed check attributes expected in 1.4 event
        if "subscribers" not in event['check']:
            event['check']['subscribers'] = event['check']['subscriptions']

        if "source" not in event['check']:
            event['check']['source'] = event['check']['proxy_entity_id']

        # Mimic 1.4 event action based on 2.0 event state
        #  action used in logs and fluentd plugins handlers
        action_state_mapping = {'flapping': 'flapping', 'passing': 'resolve',
                                'failing': 'create'}

        if "state" in event['check']:
            state = event['check']['state']
        else:
            state = "unknown::2.0_event"

        if "action" not in event and state.lower() in action_state_mapping:
            event['action'] = action_state_mapping[state.lower()]
        else:
            event['action'] = state

        # Mimic 1.4 event history based on 2.0 event history
        if "history" in event['check']:
            # save the original history
            event['check']['history_v2'] = deepcopy(event['check']['history'])
            legacy_history = []
            for history in event['check']['history']:
                if isinstance(history['status'], int):
                    legacy_history.append(str(history['status']))
                else:
                    legacy_history.append("3")

            event['check']['history'] = legacy_history

        # Setting flag indicating this function has already been called
        event['v2_event_mapped_into_v1'] = True

    # return the updated event
    return event
