#!/bin/bash

set -e

cd $(dirname $0)

echo "Testing docker build"
echo "You can change the default 'docker build' command line with the DOCKER_BUILD environment variable"
${DOCKER_BUILD:-docker build} -t doppplerr .
