#!/usr/bin/env python
import json

from sensu_plugin.tests.example_configs_utils import example_check_result_v2,\
    example_check_result_v2_mapped

from sensu_plugin.utils import map_v2_event_into_v1


EVENT = json.loads(example_check_result_v2())
EXPECTED = json.loads(example_check_result_v2_mapped())


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
