#! /bin/bash

PYTHONPATH=$(pwd) nohup python3 database/app.py > database/database.out 2> database/database.err &
