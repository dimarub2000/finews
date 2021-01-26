from .html.html_parser import BCSParser, FinamParser
import time
import json

html_sources = [BCSParser('https://bcs-express.ru/category/mirovye-rynki'),
                FinamParser('https://www.finam.ru/analysis/nslent/')]

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
    pass


def main():
    while True:
        new_data = []
        new_data += get_html_news()
        # += telegram news
        send(json.dumps(new_data))
        time.sleep(600)


if __name__ == '__main__':
    main()
