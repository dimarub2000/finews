import web_sites.html_parser as html_pars
import telegram.get_telegram_news as tg
from datetime import datetime, time
import time
import json

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, time):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

html_sources = [html_pars.BCSParser('https://bcs-express.ru/category/mirovye-rynki'),
                html_pars.FinamParser('https://www.finam.ru/analysis/nslent/')]

last_news = {'BCSParser': None, 'FinamParser': None}


# multi-threading?...
def get_html_news():
    collected_news = []
    for source in html_sources:
        res = source.get_data()
        latest_news = None
        source = source.__class__.__name__
        for news in res:
            struct_time = time.strptime(news['date'], "%m/%d/%Y, %H:%M:%S")
            if last_news[source] is None or last_news[source] < struct_time:
                collected_news.append(res)
                if latest_news is None or latest_news < struct_time:
                    latest_news = struct_time
        last_news[source] = latest_news
    return collected_news


def send(data):
    with open('channel_messages.json', 'r+') as outfile:
        messages = json.load(outfile)

        outfile.seek(0)
        for x in data:
            if x in messages:
                data.pop(x)

        messages += data
        json.dump(messages, outfile, cls=DateTimeEncoder, ensure_ascii=False)


def main():
    while True:
        new_data = []
        new_data += get_html_news()
        new_data += [tg.get_telegram_news()]
        send(new_data)
        time.sleep(600)


if __name__ == '__main__':
    main()
