#!/bin/bash

set -e

cd $(dirname $0)

echo "Downloading sonarr sub downloader"
rm -rvf sonarr-sub-downloader*
curl -L https://github.com/ebergama/sonarr-sub-downloader/archive/v0.4.zip \
        -o sonarr-sub-downloader.zip
unzip sonarr-sub-downloader.zip
echo "Setting up my environment..."
if [[ $1 == "prod" ]]; then
    pipenv install --three
else
    pipenv install --three --dev
fi
echo "Installing subdlsrv"
pipenv run pip install .
pipenv run python setup.py sdist
