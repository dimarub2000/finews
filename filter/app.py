from filter import app
import requests
from flask import request
from filter.tags_parser import TagsParser

DATABASE_URI = "http://127.0.0.1:5000"
SEARCH_URI = "http://127.0.0.1:9002"


@app.route('/', methods=['POST'])
def parse_news():
    tp = TagsParser()
    data = request.get_json()
    for news in data:
        tickers = tp.find_tags(news["text"])
        news["tags"] = tickers
    requests.post(DATABASE_URI + '/news', json=data)
    # requests.post(SEARCH_URI + '/index', json=data)
    return "OK\n"


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9001)
