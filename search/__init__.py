import os
from flask import Flask
from elastic_enterprise_search import AppSearch

app = Flask(__name__)

SEARCH_HOST = os.environ.get('SEARCH_HOST')
SEARCH_AUTH = os.environ.get('SEARCH_AUTH')
app_search = AppSearch(SEARCH_HOST, http_auth=SEARCH_AUTH)
