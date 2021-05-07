import time
import json
import requests
import parsers.lib.parser as lib_parser
import parsers.lib.web as lib_web
import parsers.lib.telegram as lib_tg

from typing import List


def init_sources() -> List[lib_parser.Source]:
    sources = [
        lib_parser.Source(
            lib_web.BCSParser('https://bcs-express.ru/category/mirovye-rynki', 5),
            'BCS',
            None,
            'html'
        ),
        lib_parser.Source(
            lib_web.FinamParser('https://www.finam.ru/analysis/nslent/', 5),
            'Finam',
            None,
            'html'
        ),
        lib_parser.Source(
            lib_web.RBKParser('https://quote.rbc.ru/', 5),
            'RBK',
            None,
            'html'
        ),
        lib_parser.Source(
            lib_tg.TgParser('https://t.me/Full_Time_Trading', 10),
            'Full Time Trading',
            None,
            'tg'
        ),
        lib_parser.Source(
            lib_tg.TgParser('https://t.me/stock_and_news', 1),
            'Financial Times',
            None,
            'tg'
        ),
        lib_parser.Source(
            lib_tg.TgParser('https://t.me/mtwits', 1),
            'Market Twits',
            None,
            'tg'
        ),
    ]
    return sources


def get_html_news(sources: List[lib_parser.Source]) -> List[dict]:
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


FILTER_SERVICE_URL = 'http://127.0.0.1:4000/'

def send(data) -> None:
    for news in data:
        print("%s, %s, %s" % (news['source'], news['time'], news['link']))
    resp = requests.post(FILTER_SERVICE_URL, json=data)
    print(resp)
    # print(requests.get('http://127.0.0.1:5000/news').text)


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
