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
from sensu_plugin.handler import SensuHandler
from sensu_plugin.utils import get_settings
from .example_configs import example_settings, example_check_result

# Currently just a single example check result
check_result = example_check_result()
check_result_dict = json.loads(check_result)
settings = example_settings()
settings_dict = json.loads(settings)

# Define some commonly mocked items for re-use with patch.object
mock_read_stdin = lambda _: check_result
mock_get_settings = lambda: settings_dict


class TestSensuHandler(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        # Instantiate a fresh SensuHandler before each test
        self.SensuHandlerTest = SensuHandler()

    def tearDown(self):
        pass

    def test_handle(self):
        exit_test = 'ignoring event -- no handler defined'
        self.assertEqual(self.SensuHandlerTest.handle(),
                      exit_test)

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

    @patch('sensu_plugin.handler.sys')
    def test_read_event(self, mocked_sys):
        '''
        Tests the read_event method
        '''

        # Mock sys.exit to do nothing
        mocked_sys.exit = lambda: {}

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
        with self.assertRaises(Exception) as context:
            read_event('astring')

    @patch.object(SensuHandler, 'read_stdin', mock_read_stdin)
    def test_deprecated_filtering_enabled(self):
        mocked_read_stdin = lambda _: check_result

        # Return True if explicilt set to True
        self.SensuHandlerTest.event = {
            'check': {
                'enable_deprecated_filtering': True
            }
        }

        self.assertTrue(
                self.SensuHandlerTest.deprecated_filtering_enabled())

        # Return False if not set
        self.SensuHandlerTest.event = {
                'check': { }
        }
        self.assertFalse(
                self.SensuHandlerTest.deprecated_filtering_enabled())

    def test_deprecated_occurrence_filtering(self):
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

    @patch.object(SensuHandler, 'read_stdin', mock_read_stdin)
    @patch('sensu_plugin.handler.get_settings', mock_get_settings)
    def test_run(self):
        '''
        Tests the run method
        '''
        pass


# Run tests
if __name__ == '__main__':
    # Run with nose directly
    import nose
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

    #unittest.main()