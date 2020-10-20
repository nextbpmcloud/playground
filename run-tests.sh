#!/bin/bash
RUNNER=pipenv
if [ -n "$1" ]
then
    RUNNER=$1
fi

DIR=test-results
mkdir -p $DIR

function msgrun() {
    echo "Running $1"
}
function msgsuccess(){
    if [ $? -ne 0 ]; then RES=fail; else RES=ok; fi
    echo "$2: $RES"
}

# run first syntax and code style checks
msgrun flake8
$RUNNER run flake8 src 2>&1 | tee $DIR/flake8.txt
msgsuccess $? flake8
$RUNNER run flake8_junit $DIR/flake8.txt $DIR/flake8_junit.xml >/dev/null

if [ "$RES" = "ok" ]; then
  # run type checks
  msgrun mypy
  $RUNNER run mypy --junit-xml $DIR/mypy_junit.xml src
  msgsuccess $? mypy
fi

if [ "$RES" = "ok" ]; then
  # run unit tests with coverage checking
  msgrun pytest
  $RUNNER run pytest --cov src --junitxml=$DIR/pytest_junit.xml
  msgsuccess $? pytest
fi

echo "Tests done."
if [ "$RES" != "ok" ]; then
    exit 1
fi
