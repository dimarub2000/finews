#! /bin/bash

PYTHONPATH=$(pwd) nohup python3 search/app.py > search/search.out 2> search/search.err &
