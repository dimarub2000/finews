#! /bin/bash

lsof -i tcp:4000 | grep -v PID | awk '{print $2}' | xargs kill
lsof -i tcp:5000 | grep -v PID | awk '{print $2}' | xargs kill
export FLASK_APP=api.py
cd filter
flask run --port=4000 > filter.log &
cd ../database
flask run --port=5000 > database.log &
cd ../
PYTHONPATH=$(pwd) python3 parsers/bin/main.py
