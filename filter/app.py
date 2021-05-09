import os
import requests

from filter import app
from flask import request
from filter.tags_parser import TagsParser
from tg_bot.msg_builder import MessageBuilder

SEARCH_URI = "http://127.0.0.1:9002"
DATABASE_URI = "http://127.0.0.1:5000"
TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']


def send_message(chat_id, text):
    url = r'https://api.telegram.org/bot{}/{}'.format(TG_BOT_TOKEN, "sendMessage")
    requests.post(url, data={"chat_id": chat_id, "text": text, "disable_web_page_preview": True})


@app.route('/', methods=['POST'])
def parse_news():
    tp = TagsParser()
    data = request.get_json()
    for news in data:
        news["tags"] = tp.find_tags(news["text"])
        resp = requests.get(DATABASE_URI + '/get_subscribers', json=news["tags"])
        for subscriber in resp.json():
            send_message(subscriber, MessageBuilder().build_message(news))

    requests.post(DATABASE_URI + '/news', json=data)
    requests.post(SEARCH_URI + '/index', json=data)
    return "OK\n"


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9001)
