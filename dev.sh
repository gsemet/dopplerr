#!/bin/bash

if [[ $1 == "install" ]]; then
    curl -L https://github.com/ebergama/sonarr-sub-downloader/archive/v0.4.zip \
            -o sonarr-sub-downloader.zip
    unzip -f sonarr-sub-downloader.zip
    pipenv install --dev --three
    pipenv lock -r
    python setup.py develop
fi

pipenv run subdlsrv -p 8000
