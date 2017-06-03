#!/bin/bash

cd $(dirname $0)
echo "Formatting python files..."
pipenv run isort -y
pipenv run yapf --recursive -i subdlsrv
