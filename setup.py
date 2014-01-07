from distutils.core import setup

setup(
    name='sensu_plugin',
    version='0.2.0',
    author='S. Zachariah Sprackett',
    author_email='zac@sprackett.com',
    packages=['sensu_plugin', 'sensu_plugin.test'],
    scripts=[],
    url='http://github.com/sensu/python_sensu_plugin/',
    license='LICENSE.txt',
    description='A framework for writing Python sensu plugins.',
    long_description="""
    """,
    install_requires=[
        'argparse'
    ],
    tests_require=[
        'pep8',
        'pylint'
    ],
)
