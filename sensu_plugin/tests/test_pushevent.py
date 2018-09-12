import socket

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

    class MockSocket(object):
        def __init__(self):
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.connect('127.0.0.1', '3030')

    # test failure when no args are passed
    with pytest.raises(ValueError):
        push_event()
