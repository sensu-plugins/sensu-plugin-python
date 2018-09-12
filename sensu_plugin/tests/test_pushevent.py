try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

import pytest

from sensu_plugin.pushevent import push_event

@patch("socket.socket", Mock())
def test_push_event():
    '''
    tests the push_event method.
    '''

    # test failure when no args are passed
    with pytest.raises(ValueError):
        push_event()
