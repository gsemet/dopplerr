#!/bin/bash

if [[ $1 == "install" ]]; then
    echo "Downloading sonarr sub downloader"
    curl -L https://github.com/ebergama/sonarr-sub-downloader/archive/v0.4.zip \
            -o sonarr-sub-downloader.zip
    unzip -f sonarr-sub-downloader.zip
    echo "Setting up my environment..."
    pipenv install --dev --three
    pipenv lock -r
    echo "Installing subdlsrv"
    pipenv run python setup.py develop
fi

pipenv run subdlsrv -p 8000
