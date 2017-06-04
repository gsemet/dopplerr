#!/bin/bash

set -e

cd $(dirname $0)

PIPENV_EXEC="pipenv run "

if [[ $1 == "bare" ]]; then
    PIPENV_EXEC=""
fi

${PIPENV_EXEC}python setup.py sdist
${PIPENV_EXEC}python setup.py flake8
echo "Running pylint"
${PIPENV_EXEC}pylint --rcfile=setup.cfg  --output-format=colorized subdlsrv
