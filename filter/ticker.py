def parse_ticker(text, start):
    if text[start].isdigit():
        return None
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
        ticker = parse_ticker(text, pos)
        if ticker is not None:
            tickers.append(ticker)
        pos = text.find('$', pos)
    return tickers
