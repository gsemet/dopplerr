#!/bin/bash

set -e

cd $(dirname $0)

echo "Test local build"

if [[ $1 == "bare" ]]; then
    PIPENV_EXEC=""
fi

${PIPENV_EXEC}python setup.py sdist bdist bdist_wheel
which pandoc 2> /dev/null > /dev/null
if [[ $? == 0 ]]; then
    echo "Updating README.md from README.rst"
    pandoc --from=rst --to=markdown --output=README.md README.rst
fi
