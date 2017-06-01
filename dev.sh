#!/bin/bash

set -e

cd $(dirname $0)

PORT=8086

echo "Starting subdlrv on port $PORT:"
pipenv run subdlsrv --port $PORT --verbose
