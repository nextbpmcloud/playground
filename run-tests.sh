#!/bin/bash
set -e

# run first syntax and code style checks
pipenv run flake8 src && echo "Flake8: ok."

# run type checks
printf "Mypy: " &&  pipenv run mypy src

# run unit tests with coverage checking
pipenv run pytest --cov src

echo "Tests done."
