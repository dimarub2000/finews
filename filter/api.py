from database import app
import requests
from flask import request
from filter.ticker_parser import TickerParser

DATABASE_URI = "http://127.0.0.1:5000"


@app.route('/', methods=['POST'])
def parse_news():
    tp = TickerParser()
    data = request.get_json()
    for news in data:
        tickers = tp.find_tickers(news["text"])
        news["tags"] = tickers
    requests.post(DATABASE_URI + '/news', json=data)
    return "OK\n"


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4000)
