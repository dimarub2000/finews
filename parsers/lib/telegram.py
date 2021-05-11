import os
import json
import parsers.lib.parser as lib_parser

from telethon import TelegramClient
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import PeerChannel
from config.config_parser import FinewsConfigParser

cfg_parser = FinewsConfigParser()
USE_MOSCOW_TIME = int(cfg_parser.get_service_setting("parsers", "use_moscow_time", 0))


class TgParser(lib_parser.Parser):
    def __init__(self, url, name, limit=1):
        super().__init__(url, name, limit)

        env_var = os.environ

        api_id = int(env_var['FINEWS_API_ID'])
        api_hash = env_var['FINEWS_API_HASH']
        self.phone = env_var['FINEWS_PHONE']
        username = env_var['FINEWS_USERNAME']

        self.client = TelegramClient(username, api_id, api_hash)

    async def process(self):
        await self.client.start()

        if self.url.isdigit():
            entity = PeerChannel(int(self.url))
        else:
            entity = self.url

        my_channel = await self.client.get_entity(entity)

        offset_id = 0
        limit = self.limit
        all_messages = []

        history = await self.client(GetHistoryRequest(
            peer=my_channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))

        messages = history.messages

        for message in messages:
            msg = message.to_dict()
            msg = {
                'text': msg['message'],
                'time': msg['date'].timestamp() + USE_MOSCOW_TIME * 3*60*60,
<<<<<<< HEAD
                'source': 'Telegram',

=======
                'source': self.name,
>>>>>>> ddda0c3c0516a418e2fab98f65cf50bc7517291e
                'link': self.url + '/' + str(msg['id'])
            }
            all_messages.append(msg)

        return all_messages

    def get_data(self):
        with self.client:
            ans_message = self.client.loop.run_until_complete(self.process())

        return json.dumps(ans_message)
