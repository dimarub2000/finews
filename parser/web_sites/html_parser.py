import json
import requests
import dateparser
from bs4 import BeautifulSoup


class HtmlParser(object):
    """Parses single html page to JSON"""
    def __init__(self, url):
        self.url = url

    def get_data(self) -> str:
        resp = requests.get(self.url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return self.parse(soup)

    def parse(self, soup) -> str:
        return json.dumps({'Parse error'})


class FinamParser(HtmlParser):
    def parse(self, soup):
        docs = []
        for news in soup.find_all('td', class_='ntitle bdotline', limit=5):
            for link in news.find_all('a', class_='f-fake-url', limit=1):
                new_url = 'https://www.finam.ru' + link.get('href')
                finam_parser = FinamCoreParser(new_url)
                res = json.loads(finam_parser.get_data())
                if res is not None:
                    docs.append(res)
        return json.dumps(docs)


class FinamCoreParser(HtmlParser):
    def parse(self, soup):
        text = soup.find('div', class_='handmade mid f-newsitem-text').get_text()
        date = dateparser.parse(soup.find('div', class_='sm lightgrey mb05 mt15').get_text()[:17]).strftime("%m/%d/%Y, %H:%M:%S")
        return json.dumps({'text': text, 'date': date, 'source': 'Finam'})


class BCSParser(HtmlParser):
    def parse(self, soup):
        docs = []
        for news in soup.find_all('a', class_='feed-item__head', limit=5):
            new_url = 'https://www.bcs-express.ru' + news.get('href')
            bcs_parser = BCSCoreParser(new_url)
            res = json.loads(bcs_parser.get_data())
            if res is not None:
                docs.append(res)
        return json.dumps(docs)


class BCSCoreParser(HtmlParser):
    def parse(self, soup):
        text = soup.find('div', class_='article__text').get_text()
        date = dateparser.parse(soup.find('div', class_='article__info-time').get_text().strip()).strftime("%m/%d/%Y, %H:%M:%S")
        return json.dumps({'text': text, 'date': date, 'source': 'BCS'})


def main():
    url = 'https://www.finam.ru/analysis/nslent/'
    parser = FinamParser(url)
    res = json.loads(parser.get_data())
    for elem in res:
        print(elem)
        print('----------------------------------')


if __name__ == '__main__':
    main()

