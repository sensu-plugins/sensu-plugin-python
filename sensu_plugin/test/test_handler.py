#!/usr/bin/env python
import unittest
from unittest.mock import patch

# Import sensu_plugin with relative path
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../../')
from sensu_plugin.handler import SensuHandler
from sensu_plugin.utils import get_settings
from example_configs import settings,check_results
import json

# Currently just a single example check result
check_result = check_results[0]


class TestSensuHandler(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        # Instantiate a fresh SensuHandler before each test
        self.SensuHandlerTest = SensuHandler()

    def tearDown(self):
        pass

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
            with self.assertRaises(ValueError) as context:
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
        with self.assertRaises(Exception):
            read_event('astring')


    def test_deprecated_filtering_enabled(self):
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


    # !!
    # WIP - Unfinished; might be removed
    # !!
    ## REMEMBER: Patch order is reversed to args order!
    #@patch('sensu_plugin.handler.get_settings')
    #@patch.object(SensuHandler, 'read_stdin')
    #def test_ready(self, 
    #        mocked_read_stdin,
    #        mocked_get_settings):
    #    '''
    #    Tests the ready method
    #    '''

    #    # Mock get_settings to return example settings
    #    mocked_get_settings.return_value = settings
    #    # Mock read_stdin with example check result
    #    mocked_read_stdin.return_value = check_result

    #    # .ready() should return settings (WIP)
    #    self.assertEqual(settings,
    #            self.SensuHandlerTest.ready())


# Run tests
if __name__ == '__main__':
    unittest.main()
