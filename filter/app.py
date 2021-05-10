import os
import requests
import logging
import time

from flask import Flask
from flask import request, Response
from multiprocessing import Pool
from filter.tags_parser import TagsParser
from tg_bot.msg_builder import MessageBuilder
from config.config_parser import FinewsConfigParser

app = Flask(__name__)

cfg_parser = FinewsConfigParser()
SEARCH_URI = cfg_parser.get_service_url('search')
DATABASE_URI = cfg_parser.get_service_url('database')
TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']
SERVICE_NAME = 'filter'

logging.basicConfig()
logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(cfg_parser.get_service_setting(SERVICE_NAME, 'log_level', 'INFO'))


def send_message(chat_id, text):
    url = r'https://api.telegram.org/bot{}/{}'.format(TG_BOT_TOKEN, "sendMessage")
    logger.info('Sending subscription to %s' % chat_id)
    requests.post(url, data={"chat_id": chat_id, "text": text, "disable_web_page_preview": True})


@app.route('/', methods=['POST'])
def parse_news():
    workers = cfg_parser.get_service_setting(SERVICE_NAME, 'num_workers', 4)
    tp = TagsParser()
    data = request.get_json()
    logger.info("Parsing data...")
    start_time = time.perf_counter()
    pool = Pool(processes=workers)
    for news in data:
        news["tags"] = tp.find_tags(news["text"])
        resp = requests.get(DATABASE_URI + '/get_subscribers', json=news["tags"])
        for subscriber in resp.json():
            pool.apply_async(send_message, args=(subscriber, MessageBuilder().build_message(news)))

    pool.close()
    elapsed_time = time.perf_counter() - start_time
    logger.info(f"Elapsed time: {elapsed_time:0.4f} seconds")
    requests.post(DATABASE_URI + '/news', json=data)
    requests.post(SEARCH_URI + '/index', json=data)
    pool.join()
    return Response(status=200)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9001)
