#!/bin/bash
BRANCH=0.1
if [ -n "$1" ]
then
    BRANCH=$1
fi
git subtree pull --prefix src/app/tests/api-spec git@github.com:nextbpmcloud/playground-api-spec $BRANCH --squash
