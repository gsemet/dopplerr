#!/bin/bash

set +e

pipenv run python setup.py flake8
pipenv run pytest subdlsrv
