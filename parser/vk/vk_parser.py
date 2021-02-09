from parser import Parser
from datetime import datetime
import vk_api
import os
import json


class VkParser(Parser):
    def __init__(self, url, limit=1):
        super().__init__(url, limit)
        login = os.getenv('vk_login')
        password = os.getenv('vk_password')
        vk_session = vk_api.VkApi(login, password)
        vk_session.auth(token_only=True)
        self.vk = vk_session.get_api()

    def get_data(self) -> str:
        resp = self.vk.wall.get(domain=self.url, count=self.limit)
        data = []
        for i in range(self.limit):
            if resp['items'][i]['marked_as_ads'] == 0:
                data.append({'text': resp['items'][i],
                             'date': datetime.utcfromtimestamp(resp['items'][i]['date']).strftime("%Y-%m-%d, %H:%M:%S"),
                             'link': self.url,
                             'source': self.url})
        return json.dumps(data)
