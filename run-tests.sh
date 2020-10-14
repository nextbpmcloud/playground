#!/bin/bash
flake8 src
mypy src
pytest --cov src
