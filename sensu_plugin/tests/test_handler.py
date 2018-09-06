#!/usr/bin/env python
import json
import os

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

import pytest

# Alter path and import modules
from sensu_plugin.handler import SensuHandler
from sensu_plugin.tests.example_configs import example_check_result
from sensu_plugin.tests.example_configs import example_settings

# Currently just a single example check result
CHECK_RESULT = example_check_result()
CHECK_RESULT_DICT = json.loads(CHECK_RESULT)
SETTINGS = example_settings()
SETTINGS_DICT = json.loads(SETTINGS)


def mock_api_settings():
    return {'host': "http://api",
            'port': 4567,
            'user': None,
            'password': None}


class TestSensuHandler(object):
    @pytest.fixture(autouse=True)
    def __init__(self):
        self.sensu_handler = None

    def setup(self):
        '''
        Instantiate a fresh SensuHandler before each test.
        '''
        self.sensu_handler = SensuHandler(autorun=False)  # noqa

    def test_handle(self):
        '''
        Tests the handle method.
        '''

        exit_msg = 'ignoring event -- no handler defined'
        assert self.sensu_handler.handle() == exit_msg

    def test_read_stdin(self):
        '''
        Tests the read_stdin method.
        '''

        # Mock reading from stdin
        with patch('sensu_plugin.handler.sys.stdin') as mocked_stdin:

            # Test with value 'sensu'
            mocked_stdin.read = lambda: 'sensu'
            assert self.sensu_handler.read_stdin() == 'sensu'

            # Test with an example check value
            mocked_stdin.read = lambda: CHECK_RESULT
            assert self.sensu_handler.read_stdin() == CHECK_RESULT
            mocked_stdin.read = None
            with pytest.raises(ValueError):
                self.sensu_handler.read_stdin()

    @patch.object(SensuHandler, 'read_stdin', CHECK_RESULT)
    def test_read_event(self):
        '''
        Tests the read_event method.
        '''

        read_event = self.sensu_handler.read_event

        # Test with dummy json
        assert isinstance(read_event('{ "sensu": "rocks" }'), dict)

        # Test with example check
        assert isinstance(read_event(CHECK_RESULT), dict)

        # Ensure that the 'client' key is present
        assert isinstance(read_event(CHECK_RESULT)['client'], dict)

        # Ensure that the 'check' key is present
        assert isinstance(read_event(CHECK_RESULT)['check'], dict)

        # Test with a string (Fail)
        with pytest.raises(Exception):
            read_event('astring')

    @patch.object(SensuHandler, 'read_stdin', CHECK_RESULT)
    def test_filtering_enabled(self):  # noqa
        '''
        Tests the deprecated_filtering_enabled method.
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

    def test_occurrence_filtering(self):  # noqa
        '''
        Tests the deprecated_occurrence_filtering method.
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
        Tests the filter method.
        '''
        self.sensu_handler.event = {'check': {}}
        dfe = 'sensu_plugin.handler.SensuHandler.deprecated_filtering_enabled'
        dof = ('sensu_plugin.handler.SensuHandler' +
               '.deprecated_occurrence_filtering')
        with patch(dfe) as deprecated_filtering_enabled:
            deprecated_filtering_enabled.return_value = True

            with patch(dof) as deprecated_occurrence_filtering:
                deprecated_occurrence_filtering.return_value = True

                self.sensu_handler.filter()

    @patch('sensu_plugin.handler.requests.post')
    @patch('sensu_plugin.handler.requests.get')
    def test_api_request(self, mock_get, mock_post):
        '''
        Tests the api_request method.
        '''

        # No api_settings defined
        with pytest.raises(AttributeError):
            self.sensu_handler.api_request('GET', 'foo')
        for mock_method, method in [(mock_get, 'GET'), (mock_post, 'POST')]:
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
            # Should supply auth
            self.sensu_handler.api_settings['password'] = 'mock_pass'
            self.sensu_handler.api_request(method, 'foo')
            mock_method.assert_called_with('http://api:4567/foo',
                                           auth=('mock_user', 'mock_pass'))

    @patch.dict(os.environ, {'SENSU_API_URL': "http://api:4567"})
    def test_get_api_settings(self):
        '''
        Tests the get_api_settings method.
        '''

        assert self.sensu_handler.get_api_settings() == mock_api_settings()

    @patch.object(SensuHandler, 'api_request')
    def test_stash_exists(self, mock_api_request):
        '''
        Tests the stash_exists method.
        '''

        class RequestsMock(object):
            def __init__(self, ret):
                self.status_code = ret

        # Mock stash exists
        mock_api_request.return_value = RequestsMock(200)
        assert self.sensu_handler.stash_exists('stash')

        # Mock stash missing
        mock_api_request.return_value = RequestsMock(404)
        assert not self.sensu_handler.stash_exists('stash')

    @patch.object(SensuHandler, 'read_stdin', Mock())
    @patch.object(SensuHandler, 'read_event', Mock())
    @patch('sensu_plugin.handler.get_settings', Mock())
    @patch.object(SensuHandler, 'get_api_settings', Mock())
    @patch.object(SensuHandler, 'filter', Mock())
    @patch.object(SensuHandler, 'handle', Mock())
    def test_run(self):
        '''
        Tests the run method.
        '''
        self.sensu_handler.run()
