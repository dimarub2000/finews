class TagsParser(object):
    def __init__(self, tag_symbol='$'):
        self.tag_symbol = tag_symbol

    @staticmethod
    def __parse_tag(text, start):
        ticker = ""
        while start != len(text) and text[start].isalpha() and text[start].isascii():
            ticker += text[start]
            start += 1
        return ticker

    def find_tags(self, text):
        tags = set()
        pos = text.find(self.tag_symbol)
        while pos != -1:
            pos += 1
            ticker = self.__parse_tag(text, pos)
            if ticker != "":
                tags.add(ticker)
            pos = text.find('$', pos)
        return list(tags)
