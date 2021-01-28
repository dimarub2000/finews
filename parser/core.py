from typing import List

import web_sites.html_parser as html_pars
import telegram.tg_parser as tg
from datetime import datetime, time
import requests
import time
import json


class Parser(object):
    def __init__(self, url, limit=1):
        self.limit = limit
        self.url = url

    def get_data(self) -> str:
        return "No data"


class Source(object):
    def __init__(self, parser, name, last_time, _type):
        self.last_time = last_time
        self.parser = parser
        self.name = name
        self.type = _type


def init_sources() -> List[Source]:
    sources = [
        Source(
            html_pars.BCSParser('https://bcs-express.ru/category/mirovye-rynki', 5),
            'BCS',
            None,
            'html'
        ),
        Source(
            html_pars.FinamParser('https://www.finam.ru/analysis/nslent/', 5),
            'Finam',
            None,
            'html'
        ),
        Source(
            html_pars.RBKParser('https://quote.rbc.ru/', 5),
            'RBK',
            None,
            'html'
        ),
        Source(
            tg.TgParser('https://t.me/Full_Time_Trading', 1),
            'Full Time Trading',
            None,
            'html'
        ),
        Source(
            tg.TgParser('https://t.me/Full_Time_Trading', 1),
            'Full Time Trading',
            None,
            'tg'
        ),
        Source(
            tg.TgParser('https://t.me/stock_and_news', 1),
            'Financial Times',
            None,
            'tg'
        )
    ]
    return sources


def get_html_news(sources: List[Source]) -> List[dict]:
    collected_news = []

    for source in sources:
        res = json.loads(source.parser.get_data())
        last_time = source.last_time

        for news in res:
            news_time = news['time']
            if source.last_time is None or source.last_time < news_time:
                collected_news.append(news)
            if last_time is None or last_time < news_time:
                last_time = news_time

        source.last_time = last_time

    return collected_news


def send(data) -> None:
    for news in data:
        print("%s, %s, %s" % (news['source'], news['time'], news['link']))
    resp = requests.post('http://127.0.0.1:5000/news', json=json.dumps(data))
    print(resp)
    print(requests.get('http://127.0.0.1:5000/news').text)


def main():
    html_sources = init_sources()
    while True:
        print('Searching for news....')
        start_time = time.perf_counter()
        data = get_html_news(html_sources)
        send(data)
        elapsed_time = time.perf_counter() - start_time
        print(f"Elapsed time: {elapsed_time:0.4f} seconds")
        time.sleep(600)


if __name__ == '__main__':
    main()
