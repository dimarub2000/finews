#! /bin/bash

PYTHONPATH=$(pwd) nohup python3 filter/app.py > filter/filter.out 2> filter/filter.err &
