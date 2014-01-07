![sensu](https://raw.github.com/sensu/sensu/master/sensu-logo.png)

# Python Sensu Plugin

This is a framework for writing your own [Sensu](https://github.com/sensu/sensu) plugins in Python.
It's not required to write a plugin (most Nagios plugins will work
without modification); it just makes it easier.

[![Build Status](https://travis-ci.org/sensu/sensu-plugin-python.png?branch=master)](https://travis-ci.org/sensu/sensu-plugin-python)

## Checks

To implement your own check, subclass SensuPluginCheck, like
this:

    from sensu_plugin import SensuPluginCheck

    class MyCheck(SensuPluginCheck):
      def setup(self):
        # Setup is called with self.parser set and is responsible for setting up
        # self.options before the run method is called

        self.parser.add_argument(
          '-w',
          '--warning',
          required=True,
          type=int,
          help='Integer warning level to output'
        )
        self.parser.add_argument(
          '-m',
          '--message',
          default=None,
          help='Message to print'
        )


      def run(self):
        # this method is called to perform the actual check

        self.check_name('my_awesome_check') # defaults to class name

        if self.options.warning == 0:
          self.ok(self.options.message)
        elif self.options.warning == 1:
          self.warning(self.options.message)
        elif self.options.warning == 2:
          self.critical(self.options.message)
        else:
          self.unknown(self.options.message)

    if __name__ == "__main__":
      f = MyCheck()

## Metrics

### JSON

    from sensu_plugin import SensuPluginMetricJSON

    class FooBarBazMetricJSON(SensuPluginMetricJSON):
        def run(self):
            self.ok({'foo': 1, 'bar': { 'baz': 'stuff' } })

    if __name__ == "__main__":
    f = FooBarBazMetricJSON()

### Graphite

    from sensu_plugin import SensuPluginMetricGraphite

    class FooBarBazMetricGraphite(SensuPluginMetricGraphite):
        def run(self):
            self.output('a', 1)
            self.output('b', 2)
            self.ok()

    if __name__ == "__main__":
    f = FooBarBazMetricGraphite()

### StatsD

    from sensu_plugin import SensuPluginMetricStatsd

    class FooBarBazMetricStatsd(SensuPluginMetricStatsd):
        def run(self):
            self.output('a', 1, 'ms')
            self.output('b.c.d', 15)
            self.ok()

    if __name__ == "__main__":
    f = FooBarBazMetricStatsd()

## License

* Based heavily on [sensu-plugin](https://github.com/sensu/sensu-plugin) Copyright 2011 Decklin Foster
* Python port Copyright 2014 S. Zachariah Sprackett

Released under the same terms as Sensu (the MIT license); see LICENSE
for details
