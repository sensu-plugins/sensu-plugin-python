import pytest

from sensu_plugin.pushevent import push_event


def test_push_event():
    '''
    tests the push_event method.
    '''

    # test failure when no args are passed
    with pytest.raises(ValueError):
        push_event()
