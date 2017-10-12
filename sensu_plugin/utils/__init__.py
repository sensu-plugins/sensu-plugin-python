import os
import json

def config_files():
  SENSU_LOADED_TEMPFILE = os.environ.get('SENSU_LOADED_TEMPFILE')
  SENSU_CONFIG_FILES = os.environ.get('SENSU_CONFIG_FILES')
  if SENSU_LOADED_TEMPFILE and os.path.isfile(SENSU_LOADED_TEMPLATE):
    with open(SENSU_LOADED_TEMPLATE, 'r') as template:
      contents = template.read()
      return contents.split(':')
  elif SENSU_CONFIG_FILES:
    return SENSU_CONFIG_FILES.split(':')
  else:
    files = ['/etc/sensu/config.json']
    [files.append('/etc/sensu/conf.d/' + filename) for filename in os.listdir('/etc/sensu/conf.d') if os.path.splitext(filename)[1] == '.json']
    return files

def get_settings():
  settings = {}
  for config_file in config_files():
    config_contents = load_config(config_file)
    if config_contents != None:
      settings = deep_merge(settings, config_contents)
  return settings 

def load_config(filename):
  try:
    with open(filename, 'r') as config_file:
      return json.loads(config_file.read())
  except:
    {}

def deep_merge(dict_one, dict_two):
  merged = dict_one.copy()
  for key,value in dict_two.items():
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

