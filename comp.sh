#!/bin/bash

#Config
GIT=$(which -a git)
PY=$(which -a python)

"$PY" "main.py" "$@"

if [ $? != 0 ]; then
    echo "Not committing, got bad return code."
    exit
fi

while true; do
    read -p "Commit? " ynq
    case $ynq in
        [Yy]* ) break;;
        [Qq]* ) quiet=true;;
        * ) exit;;
    esac
done


REAL_GIT=$(which -a git | sed -n 2p)

if [ !$quiet ]; then
	"$GIT" "commit" "-a"
else
	"$GIT" "commit" "-a -m \"Automatic Commit\""
fi
