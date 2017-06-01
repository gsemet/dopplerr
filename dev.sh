#!/bin/bash

cd $(dirname $0)

echo "Start development environment"
echo "usage: $0 <install>"
echo "  Optional argument:"
echo "    'install': create the virtualenv"

if [[ $1 == "install" ]]; then
    echo "Downloading sonarr sub downloader"
    curl -L https://github.com/ebergama/sonarr-sub-downloader/archive/v0.4.zip \
         -o sonarr-sub-downloader.zip
    unzip -f sonarr-sub-downloader.zip
    echo "Setting up my environment..."
    pipenv_version=$(pip list --format=columns | grep pipenv | cut -c 36- | sed "s/\./0/g")
    if [[ pipenv_version < 40103 ]]; then
        echo "pleae install pipenv version >= 4.1.3"
        echo "    pip install -U 'pipenv>=4.1.3'"
        exit 1
    fi
    pipenv install --dev --three
    pipenv lock
    echo "Installing subdlsrv"
    pipenv run python setup.py sdist
fi

pipenv run subdlsrv -p 8000
