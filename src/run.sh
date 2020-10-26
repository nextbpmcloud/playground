#!/bin/bash

cd app
pipenv run uvicorn main:app --host 0.0.0.0 --reload
