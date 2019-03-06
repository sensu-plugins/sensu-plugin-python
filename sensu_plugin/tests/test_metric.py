import json

from sensu_plugin import SensuPluginMetricGraphite
from sensu_plugin import SensuPluginMetricInfluxdb
from sensu_plugin import SensuPluginMetricJSON
from sensu_plugin import SensuPluginMetricStatsd

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class TestSensuPluginMetricGraphite(object):
    def __init__(self):
        self.sensu_plugin_metric = None

    def setup(self):
        '''
        Instantiate a fresh SensuPluginMetricGraphite before each test.
        '''
        self.sensu_plugin_metric = SensuPluginMetricGraphite(autorun=False)

    @patch('sensu_plugin.plugin.sys.exit', Mock())
    @patch('sys.stdout', new_callable=StringIO)
    def test_output_ok(self, out):
        self.sensu_plugin_metric.ok('sensu', 1)
        output = out.getvalue().split()
        assert output[0] == 'sensu'
        assert output[1] == '1'


class TestSensuPluginMetricInfluxdb(object):
    def __init__(self):
        self.sensu_plugin_metric = None

    def setup(self):
        '''
        Instantiate a fresh SensuPluginMetricInfluxdb before each test.
        '''
        self.sensu_plugin_metric = SensuPluginMetricInfluxdb(autorun=False)

    @patch('sensu_plugin.plugin.sys.exit', Mock())
    @patch('sys.stdout', new_callable=StringIO)
    def test_output_ok(self, out):
        self.sensu_plugin_metric.ok('sensu', 'baz=42',
                                    'env=prod,location=us-midwest')
        output = out.getvalue().split()
        assert output[0] == 'sensu,env=prod,location=us-midwest'
        assert output[1] == 'baz=42'

    @patch('sensu_plugin.plugin.sys.exit', Mock())
    @patch('sys.stdout', new_callable=StringIO)
    def test_output_ok_no_key(self, out):
        self.sensu_plugin_metric.ok('sensu', '42',
                                    'env=prod,location=us-midwest')
        output = out.getvalue().split()
        assert output[0] == 'sensu,env=prod,location=us-midwest'
        assert output[1] == 'value=42'


class TestSensuPluginMetricJSON(object):
    def __init__(self):
        self.sensu_plugin_metric = None

    def setup(self):
        '''
        Instantiate a fresh SensuPluginMetricJSON before each test.
        '''
        self.sensu_plugin_metric = SensuPluginMetricJSON(autorun=False)

    @patch('sensu_plugin.plugin.sys.exit', Mock())
    @patch('sys.stdout', new_callable=StringIO)
    def test_output_ok(self, out):
        self.sensu_plugin_metric.ok({'foo': 1, 'bar': 'anything'})
        assert json.loads(out.getvalue())


class TestSensuPluginMetricStatsd(object):
    def __init__(self):
        self.sensu_plugin_metric = None

    def setup(self):
        '''
        Instantiate a fresh SensuPluginMetricStatsd before each test.
        '''
        self.sensu_plugin_metric = SensuPluginMetricStatsd(autorun=False)

    @patch('sensu_plugin.plugin.sys.exit', Mock())
    @patch('sys.stdout', new_callable=StringIO)
    def test_output_ok(self, out):
        self.sensu_plugin_metric.ok('sensu.baz', 42, 'g')
        assert out.getvalue() == "sensu.baz:42|g\n"

    @patch('sensu_plugin.plugin.sys.exit', Mock())
    @patch('sys.stdout', new_callable=StringIO)
    def test_output_ok_two(self, out):
        self.sensu_plugin_metric.ok('sensu.baz', 42)
        assert out.getvalue() == "sensu.baz:42|kv\n"
