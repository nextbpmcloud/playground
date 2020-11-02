#!/bin/bash
BRANCH=0.1
if [ -n "$1" ]
then
    BRANCH=$1
fi
git subtree push --prefix src/app/tests/api-spec api-spec $BRANCH --squash
