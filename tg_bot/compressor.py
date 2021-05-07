class Compressor(object):
    def __init__(self, max_len=2000, num_sentences=3, redirect_msg="Подробнее читайте в источнике.\n"):
        self.max_len = max_len
        self.num_sentences = num_sentences
        self.redirect_msg = redirect_msg
        self.punctuations = {".", "!", "?"}

    def __find_new_end(self, text) -> int:
        counter = 0
        i = 0
        while i != len(text) and counter != self.num_sentences:
            if text[i] in self.punctuations:
                counter += 1
            i += 1
        return i

    def compress(self, text) -> str:
        if len(text) < self.max_len:
            return text
        new_end = self.__find_new_end(text)
        text = text[:new_end]
        text += "".join(["\n", self.redirect_msg])
        return text
