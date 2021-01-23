import requests
from bs4 import BeautifulSoup


class HtmlParser(object):
    def __init__(self, url):
        self.url = url

    def get_html_file(self):
        resp = requests.get(self.url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return self.parse(soup)

    def parse(self, soup):
        pass


class FinamParser(HtmlParser):
    def parse(self, soup):
        docs = []
        for news in soup.find_all('td', class_='ntitle bdotline', limit=5):
            for link in news.find_all('a'):
                new_url = 'https://www.finam.ru' + link.get('href')
                finam_parser = FinamCoreParser(new_url)
                res = finam_parser.get_html_file()
                if res is not None:
                    docs.append(res)
        return docs


class FinamCoreParser(HtmlParser):  # parsing refs from Finam main page
    def parse(self, soup):
        for text in soup.find_all('div', class_='handmade mid f-newsitem-text', limit=1):
            return text.get_text()


# example
url = 'https://www.finam.ru/analysis/nslent/'
parser = FinamParser(url)
res = parser.get_html_file()
for elem in res:
    print(elem)
    print('----------------------------------')
