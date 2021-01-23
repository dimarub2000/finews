import requests
from bs4 import BeautifulSoup


class HtmlParser(object):
    def __init__(self, url):
        self.url = url

    def get_html_file(self):
        resp = requests.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')
        self.parse(soup)

    def parse(self, soup):
        pass


# example
class BloombergParser(HtmlParser):
    def parse(self, soup):
        text_file = open("html.txt", "w")
        n = text_file.write(str(soup))
        text_file.close()


url = 'https://www.bloomberg.com/europe'
parser = BloombergParser(url)
parser.get_html_file()
