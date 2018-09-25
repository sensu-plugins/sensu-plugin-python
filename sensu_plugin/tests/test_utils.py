#!/usr/bin/env python
import json

try:
    from unittest.mock import patch, mock_open
except ImportError:
    from mock import patch, mock_open

from sensu_plugin.tests.example_configs_utils import example_check_result_v2,\
    example_check_result_v2_mapped

from sensu_plugin.utils import map_v2_event_into_v1, get_settings


EVENT = json.loads(example_check_result_v2())
EXPECTED = json.loads(example_check_result_v2_mapped())


def test_get_settings_no_files():
    '''
    Test the get settings method with no files.
    '''
    with patch('os.listdir') as mocked_listdir:
        mocked_listdir.return_value = []
        settings = get_settings()
        assert settings == {}


@patch('os.path.isfile')
@patch('os.path.isdir')
def test_get_settings_with_file(mock_isfile, mock_isdir):
    '''
    Test the get settings method with one file.
    '''
    test_json = '{"test": { "key": "value"}}'
    mocked_open = mock_open(read_data=test_json)
    mock_isfile.return_value = True
    mock_isdir.return_value = True
    with patch('os.listdir') as mocked_listdir:
        try:
            with patch("builtins.open", mocked_open):
                mocked_listdir.return_value = ['/etc/sensu/conf.d/test.json']
                settings = get_settings()
                assert settings == {'test': {'key': 'value'}}
        except ImportError:
            with patch("__builtin__.open", mocked_open):
                mocked_listdir.return_value = ['/etc/sensu/conf.d/test.json']
                settings = get_settings()
                assert settings == {'test': {'key': 'value'}}


def test_map_v2_into_v1_basic():
    '''
    Test the map_v2_event_into_v1 method with a basic event.
    '''

    result = map_v2_event_into_v1(EVENT)
    assert result == EXPECTED


def test_map_v2_into_v1_mapped():
    '''
    Test the map_v2_event_into_v1 method with a pre-mapped event.
    '''

    result = map_v2_event_into_v1(EVENT)
    assert result == EVENT


def test_map_v2_into_v1_nostate():
    '''
    Test the map_v2_event_into_v1 method with an event missing state.
    '''
    event = json.loads(example_check_result_v2())
    event['check'].pop('state', None)
    result = map_v2_event_into_v1(event)
    assert result['action'] == 'unknown::2.0_event'


def test_map_v2_into_v1_history():
    '''
    Test the map_v2_event_into_v1 method with invalid history.
    '''
    event = json.loads(example_check_result_v2())
    event['check']['history'].append({u'status': 'broken', u'executed': 5})
    result = map_v2_event_into_v1(event)
    assert result['check']['history'][5] == "3"
