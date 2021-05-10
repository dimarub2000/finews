class Parser(object):
    def __init__(self, url, name, limit=1):
        self.url = url
        self.name = name
        self.limit = limit

    def get_data(self) -> str:
        return "No data"


class Source(object):
    def __init__(self, parser, last_time, source_type):
        self.parser = parser
        self.last_time = last_time
        self.type = source_type

    def get_type(self):
        return self.type

    def get_last_time(self):
        return self.last_time

    def set_last_time(self, last_time):
        self.last_time = last_time

    def get_parser(self):
        return self.parser
