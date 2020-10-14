#!/bin/bash
set -e

# run first syntax and code style checks
flake8 src

# run type checks
mypy src

# run unit tests with coverage checking
pytest --cov src
