try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

import pytest

from sensu_plugin.check import SensuPluginCheck


class TestSensuPluginCheck(object):
    @pytest.fixture(autouse=True)
    def __init__(self):
        self.sensu_plugin_check = None

    def setup(self):
        '''
        Instantiate a fresh SensuPluginCheck before each test.
        '''
        self.sensu_plugin_check = SensuPluginCheck(autorun=False)

    @patch('sensu_plugin.plugin.sys.exit', Mock())
    def test_check_name(self):
        '''
        Tests the check_name method.
        '''

        # called without a name should be None
        self.sensu_plugin_check.check_name()
        self.sensu_plugin_check.ok()
        assert self.sensu_plugin_check.plugin_info['check_name'] is None

        # called with a name should set check_name
        self.sensu_plugin_check.check_name(name="checktest")
        self.sensu_plugin_check.ok()
        assert self.sensu_plugin_check.plugin_info['check_name'] == "checktest"

    def test_message(self):
        '''
        Tests the message method.
        '''
        # called without a message should return an empty tuple
        self.sensu_plugin_check.message()
        assert self.sensu_plugin_check.plugin_info['message'] == tuple()

        # called with a message should set message
        self.sensu_plugin_check.message("testing")
        assert self.sensu_plugin_check.plugin_info['message'] == ('testing',)

    def test_output(self):
        '''
        Tests the output method.
        '''
        self.sensu_plugin_check.output(args="test")
