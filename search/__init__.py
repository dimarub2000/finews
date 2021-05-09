import os
from flask import Flask
from elastic_enterprise_search import AppSearch

app = Flask(__name__)

SEARCH_HOST = os.environ['SEARCH_HOST']
SEARCH_AUTH = os.environ['SEARCH_AUTH']

app_search = AppSearch(SEARCH_HOST, http_auth=SEARCH_AUTH)
