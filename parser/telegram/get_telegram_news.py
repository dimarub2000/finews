import configparser
import json
import asyncio
from datetime import date, datetime
import time

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
    PeerChannel
)

# some functions to parse json date
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)

def create_client():
    config = configparser.ConfigParser()
    config.read("config.ini")

    api_id = config['Telegram']['api_id']  # need one acc, for now there is a problem to secure id and hash
    api_hash = str(config['Telegram']['api_hash'])
    phone = config['Telegram']['phone']
    username = config['Telegram']['username']

    client = TelegramClient(username, api_id, api_hash)

    return phone, client



async def process(phone, client, link):
    await client.start()

    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code from telegram message: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))
    #me = await client.get_me()

    user_input_channel = link;

    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

    offset_id = 0
    limit = 1  # batch
    all_messages = []
    total_messages = 0
    total_count_limit = 1  # all messages limit

    while True:
        history = await client(GetHistoryRequest(
            peer=my_channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))

        if not history.messages:
            break

        messages = history.messages

        for message in messages:
            msg = message.to_dict()
            all_messages.append(msg)

        offset_id = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    return {'text': all_messages[0]['message'], 'time': all_messages[0]['date'].strftime("%Y-%m-%d, %H:%M:%S"), # надо чекнуть приведется ли время
            'id': all_messages[0]['id'], 'source': user_input_channel}# можно вытащить ГОРАЗДО больше метаинфы


def get_telegram_news(link):
    phone, client = create_client()

    with client:
        ans_message = client.loop.run_until_complete(process(phone, client, link))

    return json.dumps([ans_message])

