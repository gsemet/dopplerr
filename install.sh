#!/bin/bash

set -e

cd $(dirname $0)

echo "Setting up my environment..."
VERSION_ARGS="--three"
if [[ $TRAVIS_PYTHON_VERSION == '2.7' ]]; then
    echo "Travis force build on Python 2.7"
    VERSION_ARGS="--two"
fi
if [[ $1 == "system" ]]; then
    pipenv install $VERSION_ARGS --system
elif [[ $1 == "system-dev" ]]; then
    pipenv install $VERSION_ARGS --system --dev
elif [[ $1 == "prod" ]]; then
    pipenv install $VERSION_ARGS
else
    pipenv install $VERSION_ARGS --dev
fi
# dopplerr is automatically installed from the "-e ." in Pipfile
echo "Done"
exit 0
