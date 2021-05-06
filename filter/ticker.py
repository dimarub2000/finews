def parse_ticker(text, start):
    ticker = ""
    while text[start].isspace() or text[start].isdigit():
        ticker += text[start]
        start += 1
    return ticker


def find_tickers(text):
    tickers = []
    pos = text.find('$')
    while pos != -1:
        pos += 1
        tickers.append(parse_ticker(text, pos))
        pos = text.find('$', pos)
    return tickers
