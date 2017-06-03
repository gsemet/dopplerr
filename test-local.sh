#!/bin/bash

set -e

cd $(dirname $0)

echo "Test local build"
pipenv run python setup.py sdist
pipenv run pytest subdlsrv
