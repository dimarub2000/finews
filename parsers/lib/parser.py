class Parser(object):
    def __init__(self, url, limit=1):
        self.limit = limit
        self.url = url

    def get_data(self) -> str:
        return "No data"


class Source(object):
    def __init__(self, parser, name, last_time, source_type):
        self.last_time = last_time
        self.parser = parser
        self.name = name
        self.type = source_type
