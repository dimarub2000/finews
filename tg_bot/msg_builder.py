class MessageBuilder(object):
    def __init__(self, compressor=None, link_format="Источик: {}\n", timestamp_format="Время Публикации: {}\n"):
        self.link_format = link_format
        self.timestamp_format = timestamp_format
        self.compressor = compressor

    def __add_link(self, text, link) -> str:
        text += "".join(["\n", self.link_format.format(link)])
        return text

    def __add_timestamp(self, text, timestamp) -> str:
        text += "".join(["\n", self.timestamp_format.format(timestamp)])
        return text

    def build_message(self, data) -> str:
        if self.compressor is not None:
            message = self.compressor.compress(data["text"])
        else:
            message = data["text"]
        message = self.__add_link(message, data["link"])
        message = self.__add_timestamp(message, data["time"])
        return message
