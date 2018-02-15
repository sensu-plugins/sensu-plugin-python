'''
Utilities for loading config files, etc.
'''

import os
import json


def config_files():
    '''
    Get list of currently used config files.
    '''
    sensu_loaded_tempfile = os.environ.get('SENSU_LOADED_TEMPFILE')
    sensu_config_files = os.environ.get('SENSU_CONFIG_FILES')
    if sensu_loaded_tempfile and os.path.isfile(sensu_loaded_tempfile):
        with open(sensu_loaded_tempfile, 'r') as tempfile:
            contents = tempfile.read()
            return contents.split(':')
    elif sensu_config_files:
        return sensu_config_files.split(':')
    else:
        files = ['/etc/sensu/config.json']
        filenames = [f for f in os.listdir('/etc/sensu/conf.d')
                     if os.path.splitext(f)[1] == '.json']
        for filename in filenames:
            files.append('/etc/sensu/conf.d/{}'.format(filename))
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


def recurse_dict(data, path, first=True):
    '''
    Get a value from within a nested dict, using a dot-separated string as
    the path, eg. 'myconfig.settings.foo' is equivalent to
    { 'myconfig': { 'settings': { 'foo': 'bar' } } } and would return 'bar'.
    '''

    # TODO: This feels dirty
    if first == True:
        path = path.split('.')
        path.reverse()

    # Take the top-most level
    current_level = path.pop()
    next_level = data.get(current_level)

    if not next_level:
        error_msg = "could not find key '{}'".format(current_level)
        raise ValueError(error_msg)

    if len(path) > 1:
        ret = recurse_dict(next_level, path, first=False)
        return ret
    # Get the last remaining tem
    elif len(path) == 1:
        return next_level.get(path[0])


def get_config(path, *configs):
    '''
    Find a dict item using dot notation, falling back to the next dict in a
    list if the item is not found. This leverages the recurse_dict function.
    '''
    found = None
    for config in configs:
        try:
            found = recurse_dict(config, path)
            break
        except ValueError as ve:
            continue

    return found