#!/bin/sh
set -x

apt update

# Module requirements
pip install requests

# Testing requiremenets
pip install pep8 pylint nose  coverage
