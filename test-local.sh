#!/bin/bash

set -e

cd $(dirname $0)

echo "Test local build"

if [[ $1 == "bare" ]]; then
    PIPENV_EXEC=""
fi

${PIPENV_EXEC}python setup.py sdist
${PIPENV_EXEC}pytest subdlsrv
