#!/usr/bin/env python
import json

from sensu_plugin.tests.example_configs import example_check_result_v2
from sensu_plugin.tests.example_configs import example_check_result_v2_mapped

from sensu_plugin.utils import map_v2_event_into_v1


def test_map_v2_event_into_v1():
    event = json.loads(example_check_result_v2())
    expected = json.loads(example_check_result_v2_mapped())

    result = map_v2_event_into_v1(event)

    assert result == expected
