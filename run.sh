export FLASK_APP=api.py
cd filter
flask run --port=4000 > filter.log &
cd ../database
flask run --port=5000 > database.log &
cd ../
PYTHONPATH=$(pwd) python3 parsers/bin/main.py
