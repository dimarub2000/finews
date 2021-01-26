from typing import List

import web_sites.html_parser as html_pars
import telegram.get_telegram_news as tg
from datetime import datetime, time
import time
import json


class Source(object):
    def __init__(self, parser, name, last_time, type):
        self.last_time = last_time
        self.parser = parser
        self.name = name
        self.type = type


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
            'https://t.me/Full_Time_Trading',
            'Full Time Trading',
            None,
            'tg'
        ),
        Source(
            'https://t.me/stock_and_news',
            'Financial Times',
            None,
            'tg'
        )
    ]
    return sources


def get_html_news(sources: List[Source]) -> List[dict]:
    collected_news = []

    for source in sources:
        res = None
        if source.type == 'html':
            res = json.loads(source.parser.get_data())
        elif source.type == 'tg':
            res = json.loads(tg.get_telegram_news(source.parser))
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
        print("%s, %s" % (news['source'], news['time']))


def main():
    html_sources = init_sources()
    while True:
        data = get_html_news(html_sources)
        send(data)
        time.sleep(600)


if __name__ == '__main__':
    main()
