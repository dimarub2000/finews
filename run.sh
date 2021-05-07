#! /bin/bash

lsof -i tcp:4000 | grep -v PID | awk '{print $2}' | xargs kill
lsof -i tcp:5000 | grep -v PID | awk '{print $2}' | xargs kill
cd filter
flask run --port=4000 > filter.out 2> filter.err & 
cd ../database
flask run --port=5000 > database.out 2> database.err &
cd ../
PYTHONPATH=$(pwd) python3 parsers/bin/main.py
