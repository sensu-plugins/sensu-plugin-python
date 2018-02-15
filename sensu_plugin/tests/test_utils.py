#!/usr/bin/env python
import unittest
import nose
from unittest.mock import patch

# Import sensu_plugin with relative path
import sys
import os
import json

# Alter path and import modules
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../../')
from sensu_plugin.utils import *
from example_configs import example_settings, example_check_result

# Currently just a single example check result
check_result = example_check_result()
check_result_dict = json.loads(check_result)
settings = example_settings()
settings_dict = json.loads(settings)

class TestSensuUtils(unittest.TestCase):
    maxDiff = None

    def test_recurse_dict(self):
        # Using example check result
        thresholds_critical = recurse_dict(check_result_dict,
                                         'check.thresholds.critical')

        self.assertEqual(thresholds_critical, 180)

        with self.assertRaises(ValueError):
            recurse_dict(check_result_dict, 'foo')

if __name__ == '__main__':
    # Run with nose directly
    module_name = sys.modules[__name__].__file__

    result = nose.run(argv=[
       sys.argv[0],
       module_name,
       '-v',
       '--with-coverage',
       '--cover-min-percentage=25',
       '--cover-erase',
       '--cover-html',
       '--cover-html-dir', './sensu_plugin/test/report',
       '--exe'
    ])