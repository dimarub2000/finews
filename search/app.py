from search import app, app_search
from flask import request


def to_dict(search_resp):
    slots = ('id', 'content', 'time', 'link', 'tags', 'source')
    res = dict()
    for slot in slots:
        res[slot] = search_resp[slot]['raw']
    return res


@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    app.logger.critical(data)
    resp = app_search.search(engine_name="finews-main", body={"query": data})
    app.logger.critical(resp)
    return "Response received"

