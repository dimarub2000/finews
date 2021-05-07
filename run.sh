#! /bin/bash

lsof -i tcp:5000 | grep -v PID | awk '{print $2}' | xargs kill
lsof -i tcp:9001 | grep -v PID | awk '{print $2}' | xargs kill
lsof -i tcp:9002 | grep -v PID | awk '{print $2}' | xargs kill

cd database
flask run --port=5000 > database.out 2> database.err &
cd ../filter
flask run --port=9001 > filter.out 2> filter.err &
cd ../search
flask run --port=9002 > search.out 2> search.err &
cd ..
PYTHONPATH=$(pwd) python3 parsers/bin/main.py
