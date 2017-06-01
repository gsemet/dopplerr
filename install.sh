#!/bin/bash

set -e

cd $(dirname $0)

echo "Downloading sonarr sub downloader"
rm -rvf sonarr-sub-downloader*
curl -L https://github.com/ebergama/sonarr-sub-downloader/archive/v0.4.zip \
        -o sonarr-sub-downloader.zip
unzip sonarr-sub-downloader.zip
echo "Setting up my environment..."
VERSION_ARGS="--three"
if [[ $TRAVIS_PYTHON_VERSION == '2.7' ]]; then
    echo "Travis force build on Python 2.7"
    VERSION_ARGS="--two"
fi
if [[ $1 == "docker" ]]; then
    pipenv install $VERSION_ARGS --system
elif [[ $1 == "prod" ]]; then
    pipenv install $VERSION_ARGS
else
    pipenv install $VERSION_ARGS --dev
fi
echo "Installing subdlsrv"
pipenv run python setup.py sdist
