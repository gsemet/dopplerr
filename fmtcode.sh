#!/bin/bash

cd $(dirname $0)
echo "Formatting python files..."
pipenv run isort -y
pipenv run autopep8 --in-place --recursive setup.py dopplerr
pipenv run yapf --recursive -i dopplerr
