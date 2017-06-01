#!/bin/bash

set -e

cd $(dirname $0)

PORT=8000

echo "Running on port $PORT"
pipenv run subdlsrv -p $PORT
