#!/bin/bash
RUNNER=pipenv
DIR=../test-results

if [ -n "$1" ]
then
    RUNNER=$1
fi

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
$RUNNER run flake8 --tee --output-file $DIR/flake8.txt app
msgsuccess $? flake8
$RUNNER run flake8_junit $DIR/flake8.txt $DIR/flake8_junit.xml >/dev/null

if [ "$RES" = "ok" ]; then
  # run type checks
  msgrun mypy
  $RUNNER run mypy --junit-xml $DIR/mypy_junit.xml app
  msgsuccess $? mypy
fi

if [ "$RES" = "ok" ]; then
  # run unit tests with coverage checking
  msgrun pytest
  $RUNNER run pytest --cov app --junitxml=$DIR/pytest_junit.xml
  msgsuccess $? pytest
fi

echo "Tests done."
if [ "$RES" != "ok" ]; then
    exit 1
fi
pipenv run coverage html
pipenv run coverage xml
echo "Downloading coverage uploader"
curl -s https://codecov.io/bash > upload_codecov
chmod +x upload_codecov
./upload_codecov -f coverage.xml
mv htmlcov coverage.xml $DIR
