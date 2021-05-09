#! /bin/bash

lsof -i tcp:5000 | grep -v PID | awk '{print $2}' | xargs kill
lsof -i tcp:9001 | grep -v PID | awk '{print $2}' | xargs kill
lsof -i tcp:9002 | grep -v PID | awk '{print $2}' | xargs kill

export PYTHONPATH=$(pwd)
python3 database/app.py > database.out 2> database.err &
python3 filter/app.py > filter.out 2> filter.err &
python3 search/app.py > search.out 2> search.err &
python3 parsers/bin/main.py
