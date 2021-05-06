from database import app
import requests
from flask import request
from filter.ticker import find_tickers

DATABASE_URI = "http://127.0.0.1:5000"


@app.route('/', methods=['POST'])
def parse_news():
    data = request.get_json()
    for news in data:
        tickers = find_tickers(news["text"])
        news["tags"] = tickers
    requests.post(DATABASE_URI + '/news', json=data)


if __name__ == '__main__':
    app.run()
