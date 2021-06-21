#! /bin/bash

PYTHONPATH=$(pwd) nohup python3 parsers/bin/app.py > parsers/parsers.out 2> parsers/parsers.err &
