from typing import List

import web_sites.html_parser as html_pars
# import telegram.get_telegram_news as tg
from datetime import datetime, time
import time
import json


class HtmlSource(object):
    def __init__(self, parser, name, last_time):
        self.last_time = last_time
        self.parser = parser
        self.name = name


def init_html_sources() -> List[HtmlSource]:
    html_sources = [
        HtmlSource(
            html_pars.BCSParser('https://bcs-express.ru/category/mirovye-rynki', 5),
            'BCS',
            None,
        ),
        HtmlSource(
            html_pars.FinamParser('https://www.finam.ru/analysis/nslent/', 5),
            'Finam',
            None,
        ),
    ]
    return html_sources


def get_html_news(html_sources: List[HtmlSource]) -> List[dict]:
    collected_news = []

    for html_source in html_sources:
        res = json.loads(html_source.parser.get_data())
        last_time = html_source.last_time

        for news in res:
            news_time = news['time']
            if html_source.last_time is None or html_source.last_time < news_time:
                collected_news.append(news)
            if last_time is None or last_time < news_time:
                last_time = news_time

        html_source.last_time = last_time

    return collected_news


# class DateTimeEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, datetime):
#             return o.isoformat()
#         if isinstance(o, time):
#             return o.isoformat()
#         return json.JSONEncoder.default(self, o)
#
#
# def send(data):
#     with open('channel_messages.json', 'r+') as outfile:
#         messages = json.load(outfile)
#
#         outfile.seek(0)
#         for x in data:
#             if x in messages:
#                 data.pop(x)
#
#         messages += data
#         json.dump(messages, outfile, cls=DateTimeEncoder, ensure_ascii=False)

def send(data) -> None:
    for news in data:
        print("%s, %s" % (news['source'], news['time']))


def main():
    html_sources = init_html_sources()
    while True:
        data = get_html_news(html_sources)
        send(data)
        time.sleep(600)


if __name__ == '__main__':
    main()
