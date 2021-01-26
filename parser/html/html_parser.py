import requests
from bs4 import BeautifulSoup
import dateparser


class HtmlParser(object):
    def __init__(self, url):
        self.url = url

    def get_data(self):
        resp = requests.get(self.url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return self.parse(soup)

    def parse(self, soup):
        pass


class FinamParser(HtmlParser):
    def parse(self, soup):
        docs = []
        for news in soup.find_all('td', class_='ntitle bdotline', limit=5):
            for link in news.find_all('a', class_='f-fake-url', limit=1):
                new_url = 'https://www.finam.ru' + link.get('href')
                finam_parser = FinamCoreParser(new_url)
                res = finam_parser.get_data()
                if res is not None:
                    docs.append(res)
        return docs


class FinamCoreParser(HtmlParser):  # parsing refs from Finam main page
    def parse(self, soup):
        text = soup.find('div', class_='handmade mid f-newsitem-text')
        date = dateparser.parse(soup.find('div', class_='sm lightgrey mb05 mt15').get_text()[:17]).strftime("%m/%d/%Y, %H:%M:%S")
        return {'text': text.get_text(), 'source': 'Finam', 'date': date}


class BCSParser(HtmlParser):
    def parse(self, soup):
        docs = []
        for news in soup.find_all('a', class_='feed-item__head', limit=5):
            new_url = 'https://www.bcs-express.ru' + news.get('href')
            bcs_parser = BCSCoreParser(new_url)
            res = bcs_parser.get_data()
            if res is not None:
                docs.append(res)
        return docs


class BCSCoreParser(HtmlParser):
    def parse(self, soup):
        text = soup.find('div', class_='article__text')
        date = dateparser.parse(soup.find('div', class_='article__info-time').get_text().strip()).strftime("%m/%d/%Y, %H:%M:%S")
        return {'text': text.get_text(), 'date': date, 'source': 'BCS'}


# example
url = 'https://www.finam.ru/analysis/nslent/'
parser = FinamParser(url)
res = parser.get_data()
for elem in res:
    print(elem)
    print('----------------------------------')
