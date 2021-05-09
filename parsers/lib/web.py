import os
import json
import requests
import dateparser
import parsers.lib.parser as lib_parser
from config.config_parser import FinewsConfigParser

from bs4 import BeautifulSoup

cfg_parser = FinewsConfigParser()
ASSUME_WEB_MOSCOW = int(cfg_parser.get_service_setting("parsers", "use_moscow_time"))


class HtmlParser(lib_parser.Parser):
    """Parses single html page to JSON"""

    def __init__(self, url, limit=1):
        super().__init__(url, limit)

    def get_data(self) -> str:
        resp = requests.get(self.url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return self.parse(soup)

    def parse(self, soup) -> str:
        return json.dumps({'Parse error'})

    @staticmethod
    def format_time(date_data) -> int:
        return date_data.timestamp() - 3 * 60 * 60 * ASSUME_WEB_MOSCOW


class FinamParser(HtmlParser):
    def parse(self, soup):
        docs = []
        for news in soup.find_all('td', class_='ntitle bdotline', limit=self.limit):
            for link in news.find_all('a', class_='f-fake-url', limit=1):
                new_url = 'https://www.finam.ru' + link.get('href')
                finam_parser = FinamCoreParser(new_url)
                res = json.loads(finam_parser.get_data())
                if res is not None:
                    docs.append(res)
        return json.dumps(docs)


class FinamCoreParser(HtmlParser):
    def parse(self, soup):
        text = soup.find('div', class_='handmade mid f-newsitem-text').get_text().strip()
        time = self.format_time(dateparser.parse(
            soup.find('div', class_='sm lightgrey mb05 mt15').get_text()[:17],
            settings={'DATE_ORDER': 'DMY'}
        ))
        return json.dumps({'text': text, 'time': time, 'source': 'Finam', 'link': self.url})


class BCSParser(HtmlParser):
    def parse(self, soup):
        docs = []
        for news in soup.find_all('a', class_='feed-item__head', limit=self.limit):
            new_url = 'https://www.bcs-express.ru' + news.get('href')
            bcs_parser = BCSCoreParser(new_url)
            res = json.loads(bcs_parser.get_data())
            if res is not None:
                docs.append(res)
        return json.dumps(docs)


class BCSCoreParser(HtmlParser):
    def parse(self, soup):
        text = soup.find('div', class_='article__text').get_text().strip()
        time = self.format_time(dateparser.parse(soup.find('div', class_='article__info-time').get_text().strip()))
        return json.dumps({'text': text, 'time': time, 'source': 'BCS', 'link': self.url})


class RBKParser(HtmlParser):
    def parse(self, soup):
        docs = []
        for news in soup.find_all('div', class_='q-item js-load-item', limit=5):
            time = self.format_time(dateparser.parse(news.find('span', class_='q-item__date__text').get_text().strip()))
            link = news.find('a', class_='q-item__link').get('href')
            text = '%s.\n%s.\nПодробнее: %s' % (
                news.find('span', class_='q-item__title').get_text().strip(),
                news.find('span', class_='q-item__description').get_text().strip(),
                link
            )
            docs.append({'text': text, 'time': time, 'source': 'RBK', 'link': link})
        return json.dumps(docs)


def main():
    url = 'https://quote.rbc.ru/'
    parser = RBKParser(url)
    res = json.loads(parser.get_data())
    for elem in res:
        print(elem)


if __name__ == '__main__':
    main()
