import configparser
import json
import asyncio
from datetime import date, datetime
import time

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import PeerChannel


class TgParser(object):
    def __init__(self, url, limit=1):
        config = configparser.ConfigParser()
        config.read("config.ini")

        api_id = config['Telegram']['api_id']  # need one acc, for now there is a problem to secure id and hash
        api_hash = str(config['Telegram']['api_hash'])
        self.phone = config['Telegram']['phone']
        username = config['Telegram']['username']

        self.client = TelegramClient(username, api_id, api_hash)
        self.url = url
        self.limit = limit

    async def process(self):
        await self.client.start()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone)
            try:
                await self.client.sign_in(self.phone, input('Enter the code from telegram message: '))
            except SessionPasswordNeededError:
                await self.client.sign_in(password=input('Password: '))

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
                'time': msg['date'].strftime("%Y-%m-%d, %H:%M:%S"),
                'source': 'Telegram',
                'link': self.url
            }
            all_messages.append(msg)

        return all_messages

    def get_data(self):
        with self.client:
            ans_message = self.client.loop.run_until_complete(self.process())

        return json.dumps(ans_message)


