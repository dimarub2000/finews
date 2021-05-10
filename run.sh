#! /bin/bash

lsof -i tcp:5000 | grep -v PID | awk '{print $2}' | xargs kill
lsof -i tcp:9001 | grep -v PID | awk '{print $2}' | xargs kill
lsof -i tcp:9002 | grep -v PID | awk '{print $2}' | xargs kill

export PYTHONPATH=$(pwd)
nohup python3 filter/app.py > filter/filter.out 2> filter/filter.err &
nohup python3 search/app.py > search/search.out 2> search/search.err &
nohup python3 database/app.py > database/database.out 2> database/database.err &
python3 parsers/bin/main.py
