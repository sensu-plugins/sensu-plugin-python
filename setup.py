from distutils.core import setup

setup(
    name='sensu_plugin',
    version='0.4.7',
    author='Sensu-Plugins and contributors',
    author_email='sensu-users@googlegroups.com',
    packages=['sensu_plugin', 'sensu_plugin.test'],
    scripts=[],
    url='https://github.com/sensu-plugins/sensu-plugin-python',
    license='LICENSE.txt',
    description='A framework for writing Python sensu plugins.',
    long_description="""
    """,
    install_requires=[
        'argparse',
        'requests'
    ],
    tests_require=[
        'pep8',
        'pylint'
    ],
)
