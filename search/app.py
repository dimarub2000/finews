import json
import os
import logging
from flask import Flask
from elastic_enterprise_search import AppSearch
from flask import request, Response

from config.config_parser import FinewsConfigParser

app = Flask(__name__)

SEARCH_HOST = os.environ['SEARCH_HOST']
SEARCH_AUTH = os.environ['SEARCH_AUTH']
SERVICE_NAME = 'search'
cfg_parser = FinewsConfigParser()
app_search = AppSearch(SEARCH_HOST, http_auth=SEARCH_AUTH)

logging.basicConfig()
logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(cfg_parser.get_log_level(SERVICE_NAME, 'INFO'))
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S"))
logger.addHandler(ch)
score_treshold = cfg_parser.get_service_settings(SERVICE_NAME)["score"]


def to_dict(result):
    slots = ('id', 'text', 'time', 'link', 'tags', 'source')
    res = dict()
    for slot in slots:
        res[slot] = result[slot]['raw']
    res['score'] = result['_meta']['score']
    return res


def response_to_list(response):
    return sorted(list(filter(lambda item: item['score'] >= score_treshold,
                              list(map(lambda result: to_dict(result),
                                       response.get('results', []))))),
                  key=lambda data: data['time'], reverse=True)


@app.route('/search', methods=['GET'])
def search():
    limit = request.args.get('limit', default=1, type=int)
    data = request.get_json()
    search_resp = app_search.search(engine_name="finews-main", body={"query": data})
    response_list = response_to_list(search_resp)[:limit]
    if len(response_list) == 0:
        logger.debug('Not found news for request: {}'.format(data))
        return Response(status=404)
    return Response(json.dumps(response_list), status=200)


@app.route('/index', methods=['POST'])
def index():
    pass
    #data = request.get_json()
    #app_search.index_documents(engine_name="finews-main", documents=data)
    #return "Indexed to Elasticsearch {} documents".format(len(data))


@app.route('/ping', methods=['GET'])
def ping():
    logger.info("PING")
    return Response(status=200)


if __name__ == "__main__":
    app.run(port=9002)
