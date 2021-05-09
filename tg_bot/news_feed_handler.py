class NewsFeedHandler(object):
    def __init__(self, data, page_size=5):
        self.data = data
        self.page_size = page_size
        self.current_offset = 0

    def get_new_page(self):
        page = self.data[self.current_offset:self.current_offset+self.page_size]
        if len(page) == 0:
            return None
        self.current_offset += self.page_size
        return page
