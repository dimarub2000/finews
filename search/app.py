import json

from search import app, app_search
from flask import request


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

