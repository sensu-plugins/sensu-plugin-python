#!/bin/sh
set -x

apt-get update

# Module requirements
pip install requests

# Testing requiremenets
pip install pycodestyle pylint nose coverage mock pytest

# running in docker
touch /docker
