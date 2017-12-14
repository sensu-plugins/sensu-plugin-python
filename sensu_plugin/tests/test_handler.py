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
import pytest

# Currently just a single example check result
check_result = example_check_result()
check_result_dict = json.loads(check_result)
settings = example_settings()
settings_dict = json.loads(settings)

#
# TODO:
#   - Why can't I just mock read_event instead of sys for run()?
#

# Some commonly mocked items for re-use with patch.object
def mock_read_stdin():
    return check_result

def mock_get_settings():
    return settings_dict

def mock_api_settings():
    return {
                'host': 'http://api',
                'port': 4567,
                'user': None,
                'password': None
            }


class TestSensuHandler(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        '''
        Instantiate a fresh SensuHandler before each test
        '''
        SensuHandler.autorun = False
        self.sensu_handler = SensuHandler()

    def test_handle(self):
        '''
        Tests the handle method
        '''

        exit_msg = 'ignoring event -- no handler defined'
        assert self.sensu_handler.handle() == exit_msg

    def test_read_stdin(self):
        '''
        Tests the read_stdin method
        '''

        # Mock reading from stdin
        with patch('sensu_plugin.handler.sys.stdin') as mocked_stdin:
            # Test with value 'sensu'
            mocked_stdin.read = lambda: 'sensu'
            assert self.sensu_handler.read_stdin() == 'sensu'

            # Test with an example check value
            mocked_stdin.read = lambda: check_result
            assert self.sensu_handler.read_stdin() == check_result

            mocked_stdin.read = None
            with pytest.raises(ValueError):
                self.sensu_handler.read_stdin()

    @patch.object(SensuHandler, 'read_stdin', mock_read_stdin)
    def test_read_event(self):
        '''
        Tests the read_event method
        '''

        read_event = self.sensu_handler.read_event

        # Test with dummy json
        assert isinstance(
                read_event('{ "sensu": "rocks" }'),
                dict)

        # Test with example check
        assert isinstance(
                read_event(check_result),
                dict)

        # Ensure that the 'client' key is present
        assert isinstance(
                read_event(check_result)['client'],
                dict)

        # Ensure that the 'check' key is present
        assert isinstance(
                read_event(check_result)['check'],
                dict)

        # Test with a string (Fail)
        with pytest.raises(Exception):
            read_event('astring')

    @patch.object(SensuHandler, 'read_stdin', mock_read_stdin)
    def test_deprecated_filtering_enabled(self):
        '''
        Tests the deprecated_filtering_enabled method
        '''

        # Return True if explicilt set to True
        self.sensu_handler.event = {
            'check': {'enable_deprecated_filtering': True}
        }

        assert self.sensu_handler.deprecated_filtering_enabled()

        # Return False if not set
        self.sensu_handler.event = {
                'check': {}
        }
        assert not self.sensu_handler.deprecated_filtering_enabled()

    def test_deprecated_occurrence_filtering(self):
        '''
        Tests the deprecated_occurrence_filtering method
        '''

        self.sensu_handler.event = {
            'check': {
                'enable_deprecated_occurrence_filtering': True
            }
        }
        assert self.sensu_handler.deprecated_occurrence_filtering()

        self.sensu_handler.event = {
            'check': {}
        }
        assert not self.sensu_handler.deprecated_occurrence_filtering()

    @patch.object(SensuHandler, 'filter_disabled', Mock())
    @patch.object(SensuHandler, 'filter_silenced', Mock())
    @patch.object(SensuHandler, 'filter_dependencies', Mock())
    @patch.object(SensuHandler, 'filter_repeated', Mock())
    def test_filter(self):
        '''
        Tests the filter method
        '''

        with patch('sensu_plugin.handler.SensuHandler.deprecated_filtering_enabled') as deprecated_filtering_enabled:
            deprecated_filtering_enabled.return_value = True
            self.sensu_handler.filter_disabled.assert_called
            self.sensu_handler.filter_silenced.assert_called
            self.sensu_handler.filter_dependencies.assert_called

            with patch('sensu_plugin.handler.SensuHandler.deprecated_occurrence_filtering') as deprecated_occurrence_filtering:
                deprecated_occurrence_filtering.return_value = True
                self.sensu_handler.filter_repeated.assert_called

                self.sensu_handler.filter()

    @patch('sensu_plugin.handler.requests.post')
    @patch('sensu_plugin.handler.requests.get')
    def test_api_request(self, mock_get, mock_post):
        '''
        Tests the api_request method
        '''

        # No api_settings defined
        with pytest.raises(AttributeError):
            self.sensu_handler.api_request('GET', 'foo')

        for mock_method, method in [(mock_get,'GET'),(mock_post,'POST')]:
            # Should not supply auth
            self.sensu_handler.api_settings = {
                'host': 'http://api',
                'port': 4567
            }
            self.sensu_handler.api_request(method, 'foo')
            mock_method.assert_called_with('http://api:4567/foo', auth=())

            # Should still not supply any auth as it requires password too
            self.sensu_handler.api_settings['user'] = 'mock_user'
            self.sensu_handler.api_request(method, 'foo')
            mock_method.assert_called_with('http://api:4567/foo', auth=())
#
            ## Should supply auth
            self.sensu_handler.api_settings['password'] = 'mock_pass'
            self.sensu_handler.api_request(method, 'foo')
            mock_method.assert_called_with('http://api:4567/foo', auth=('mock_user', 'mock_pass'))

    @patch.object(SensuHandler, 'api_request')
    def test_stash_exists(self, mock_api_request):
        '''
        Tests the stash_exists method
        '''
        class RequestsMock(object):
            def __init__(self, ret):
                self.status_code = ret

        # Mock stash exists
        mock_api_request.return_value = RequestsMock(200)
        assert self.sensu_handler.stash_exists('stash') == True

        # Mock stash missing
        mock_api_request.return_value = RequestsMock(404)
        assert self.sensu_handler.stash_exists('stash') == False

    def test_get_api_settings(self):
        '''
        Tests the get_api_settings method
        '''

        # Mock getting SENSU_API_URL environment var
        with patch('sensu_plugin.handler.os.environ') as mocked_environ:
            mocked_environ.get = lambda _: 'http://api:4567'
            assert self.sensu_handler.get_api_settings() == mock_api_settings()

        # Load example settings and use those
        self.sensu_handler.settings = settings_dict
        assert self.sensu_handler.get_api_settings() == settings_dict['api']

    @patch.object(SensuHandler, 'read_stdin', Mock())
    @patch.object(SensuHandler, 'read_event', Mock())
    #@patch('sensu_plugin.handler.sys', Mock()) # Why is this required?!
    @patch('sensu_plugin.handler.get_settings', Mock())
    @patch.object(SensuHandler, 'get_api_settings', Mock())
    @patch.object(SensuHandler, 'filter', Mock())
    @patch.object(SensuHandler, 'handle', Mock())
    def test_run(self):
        '''
        Tests the run method
        '''
        # TODO: Improve?
        self.sensu_handler.run()
        self.sensu_handler.read_stdin.assert_called
        self.sensu_handler.read_event.assert_called
        self.sensu_handler.get_api_settings.assert_called
        self.sensu_handler.filter.assert_called
        self.sensu_handler.handle.assert_called

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