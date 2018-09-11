try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import pytest

from sensu_plugin.plugin import SensuPlugin


def mock_plugin_info():
    return {'check_name': None, 'message': None, 'status': None}


class TestSensuPlugin(object):
    @pytest.fixture(autouse=True)
    def __init__(self):
        self.sensu_plugin = None

    def setup(self):
        '''
        Instantiate a fresh SensuPlugin before each test.
        '''
        self.sensu_plugin = SensuPlugin(autorun=False)

    def test_plugin_info(self):
        '''
        Tests the values of plugin_info.
        '''
        assert self.sensu_plugin.plugin_info == mock_plugin_info()

    def test_run_exit_code(self):
        '''
        Tests the exit status of run.
        '''
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            self.sensu_plugin.run()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    @patch('sensu_plugin.plugin.sys.exit', Mock())
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_stdout(self, out):
        '''
        Tests the the correct text values returns from run.
        '''
        self.sensu_plugin.run()
        expected = ("SensuPlugin: Not implemented! " +
                    "You should override SensuPlugin.run()")
        assert expected in out.getvalue()
