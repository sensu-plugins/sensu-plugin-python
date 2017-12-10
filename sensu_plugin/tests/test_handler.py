#!/usr/bin/env python
import unittest
from mock import Mock
from unittest.mock import patch

# Import sensu_plugin with relative path
import sys
import os
import json

# Alter path and import modules
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../../')
from sensu_plugin.handler import SensuHandler
from sensu_plugin.utils import get_settings
from example_configs import example_settings, example_check_result

import nose

# Currently just a single example check result
check_result = example_check_result()
check_result_dict = json.loads(check_result)
settings = example_settings()
settings_dict = json.loads(settings)

# Define some commonly mocked items for re-use with patch.object
mock_read_stdin = lambda _: check_result
mock_get_settings = lambda: settings_dict

#
# TODO:
#   - Why can't I just mock read_event instead of sys?
#

class TestSensuHandler(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        # Instantiate a fresh SensuHandler before each test
        SensuHandler.autorun = False
        self.SensuHandlerTest = SensuHandler()

    def tearDown(self):
        pass

    def test_handle(self):
        '''
        Tests the handle method
        '''

        exit_msg = 'ignoring event -- no handler defined'
        self.assertEqual(self.SensuHandlerTest.handle(),
                         exit_msg)

    def test_read_stdin(self):
        '''
        Tests the read_stdin method
        '''

        # Mock reading from stdin
        with patch('sensu_plugin.handler.sys.stdin') as mocked_stdin:
            # Test with value 'sensu'
            mocked_stdin.read = lambda: 'sensu'
            self.assertIs('sensu', self.SensuHandlerTest.read_stdin())

            # Test with an example check value
            mocked_stdin.read = lambda: check_result
            self.assertIs(check_result, self.SensuHandlerTest.read_stdin())

            mocked_stdin.read = None
            with self.assertRaises(ValueError):
                self.SensuHandlerTest.read_stdin()

    @patch.object(SensuHandler, 'read_stdin', mock_read_stdin)
    def test_read_event(self):
        '''
        Tests the read_event method
        '''

        read_event = self.SensuHandlerTest.read_event

        # Test with dummy json
        self.assertIsInstance(
                read_event('{ "sensu": "rocks" }'),
                dict)

        # Test with example check
        self.assertIsInstance(
                read_event(check_result),
                dict)

        # Ensure that the 'client' key is present
        self.assertIsInstance(
                read_event(check_result)['client'],
                dict)

        # Ensure that the 'check' key is present
        self.assertIsInstance(
                read_event(check_result)['check'],
                dict)

        # Test with a string (Fail)
        with self.assertRaises(Exception):
            read_event('astring')

    @patch.object(SensuHandler, 'read_stdin', mock_read_stdin)
    def test_deprecated_filtering_enabled(self):
        '''
        Tests the deprecated_filtering_enabled method
        '''

        # Return True if explicilt set to True
        self.SensuHandlerTest.event = {
            'check': { 'enable_deprecated_filtering': True }
        }

        self.assertTrue(
                self.SensuHandlerTest.deprecated_filtering_enabled())

        # Return False if not set
        self.SensuHandlerTest.event = {
                'check': {}
        }
        self.assertFalse(
                self.SensuHandlerTest.deprecated_filtering_enabled())



    def test_deprecated_occurrence_filtering(self):
        '''
        Tests the deprecated_occurrence_filtering method
        '''

        self.SensuHandlerTest.event = {
            'check': {
                'enable_deprecated_occurrence_filtering': True
            }
        }
        self.assertTrue(
            self.SensuHandlerTest.deprecated_occurrence_filtering())

        self.SensuHandlerTest.event = {
            'check': {}
        }
        self.assertFalse(
            self.SensuHandlerTest.deprecated_occurrence_filtering()
        )

    def test_get_api_settings(self):
        '''
        Tests the get_api_settings method
        '''

        # Mock getting SENSU_API_URL environment var
        with patch('sensu_plugin.handler.os.environ') as mocked_environ:
            mocked_environ.get = lambda _: 'http://api:4567'
            desired_api_settings = {
                'host': 'http//api',
                'port': 4567,
                'user': None,
                'password': None
            }

            self.assertEqual(self.SensuHandlerTest.get_api_settings(),
                    desired_api_settings)

        # Load example settings and use those
        settings_dict = json.loads(settings)
        self.SensuHandlerTest.settings = settings_dict

        self.assertEqual(self.SensuHandlerTest.get_api_settings(),
                    settings_dict['api'])

    @patch.object(SensuHandler, 'read_stdin', Mock())
    @patch.object(SensuHandler, 'read_event', Mock())
    @patch('sensu_plugin.handler.sys', Mock()) # Why is this required?!
    @patch('sensu_plugin.handler.get_settings', Mock())
    @patch.object(SensuHandler, 'get_api_settings', Mock())
    @patch.object(SensuHandler, 'filter', Mock())
    @patch.object(SensuHandler, 'handle', Mock())
    def test_run(self):
        '''
        Tests the run method
        '''
        # TODO: Improve?
        self.SensuHandlerTest.run()
        self.SensuHandlerTest.read_stdin.assert_called
        self.SensuHandlerTest.read_event.assert_called
        self.SensuHandlerTest.get_api_settings.assert_called
        self.SensuHandlerTest.filter.assert_called
        self.SensuHandlerTest.handle.assert_called


# Run tests
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
       '--cover-html-dir',
       '{}/report'.format(
           os.path.dirname(os.path.realpath(__file__))),
       '--exe'
    ])

    #unittest.main()