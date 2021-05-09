import json
import os
from flask import Flask
from elastic_enterprise_search import AppSearch
from flask import request

app = Flask(__name__)

SEARCH_HOST = os.environ['SEARCH_HOST']
SEARCH_AUTH = os.environ['SEARCH_AUTH']

app_search = AppSearch(SEARCH_HOST, http_auth=SEARCH_AUTH)


def to_dict(result):
    slots = ('id', 'text', 'time', 'link', 'tags', 'source')
    res = dict()
    for slot in slots:
        res[slot] = result[slot]['raw']
    return res


def response_to_list(response):
    return list(map(lambda result: to_dict(result), response.get('results', [])))


@app.route('/search', methods=['GET'])
def search():
    limit = request.args.get('limit', default=1, type=int)
    data = request.get_json()
    search_resp = app_search.search(engine_name="finews-main", body={"query": data})
    return json.dumps(response_to_list(search_resp)[:limit])


@app.route('/index', methods=['POST'])
def index():
    data = request.get_json()
    app_search.index_documents(engine_name="finews-main", documents=data)
    return "Indexed to Elasticsearch {} documents".format(len(data))


if __name__ == "__main__":
    app.run(port=9002)
