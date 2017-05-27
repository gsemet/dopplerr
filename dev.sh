#!/bin/bash

if [[ $1 == "install" ]]; then
    curl -L https://github.com/ebergama/sonarr-sub-downloader/archive/v0.4.zip \
            -o sonarr-sub-downloader.zip
    unzip -f sonarr-sub-downloader.zip
    pipenv --three
    pipenv lock -r
    pipenv install
fi


pipenv run python proxy.py -p 8000
