#!/bin/bash
set -e

# run first syntax and code style checks
pipenv run flake8 src

# run type checks
pipenv run mypy src

# run unit tests with coverage checking
pipenv run pytest --cov src
