#!/bin/bash

set -e

cd $(dirname $0)

echo "Building..."

if [[ $1 == "bare" ]]; then
    PIPENV_EXEC=""
fi

${PIPENV_EXEC}pytest subdlsrv
