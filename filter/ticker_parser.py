import string


class TickerParser(object):
    def __init__(self, ticker_symbol='$'):
        self.ticker_symbol = ticker_symbol

    def __parse_ticker(self, text, start):
        if text[start].isdigit():
            return None
        ticker = ""
        while start != len(text) and not text[start].isspace() and (text[start] not in string.punctuation):
            ticker += text[start]
            start += 1
        return ticker

    def find_tickers(self, text):
        tickers = set()
        pos = text.find('$')
        while pos != -1:
            pos += 1
            ticker = self.__parse_ticker(text, pos)
            if ticker is not None:
                tickers.add(ticker)
            pos = text.find('$', pos)
        return list(tickers)