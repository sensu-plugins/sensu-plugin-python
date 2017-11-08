#!/bin/sh

EXIT=0
pep8 sensu_plugin
RC=$?
if [ $RC -ne 0 ]; then
  EXIT=1
fi
pylint --rcfile=pylint.rc sensu_plugin
RC=$?
if [ $RC -ne 0 ]; then
  EXIT=1
fi
nosetests --with-coverage --cover-package=sensu_plugin \
  --cover-min-percentage=25 sensu_plugin/test/
RC=$?
if [ $RC -ne 0 ]; then
  EXIT=1
fi

echo
echo "Exiting with code $EXIT"
exit $EXIT
