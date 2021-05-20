import time
import json
import requests
import logging
import parsers.lib.parser as lib_parser
from parsers.lib.parser import Source
import parsers.lib.web as lib_web
import parsers.lib.telegram as lib_tg
from config.config_parser import FinewsConfigParser
from multiprocessing import Pool, Manager
from multiprocessing.managers import BaseManager

from typing import List

cfg_parser = FinewsConfigParser()
FILTER_SERVICE_URL = cfg_parser.get_service_url('filter')
DATABASE_URL = cfg_parser.get_service_url('database')
SERVICE_NAME = 'parsers'

logging.basicConfig()
logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(cfg_parser.get_log_level(SERVICE_NAME, 'INFO'))
telegram_timeout = 0


def get_last_time(source):
    resp = requests.get(DATABASE_URL + '/last_time?source={}'.format(source))
    if resp.status_code == requests.codes.OK:
        return resp.json()
    return None


def init_sources() -> List:
    BaseManager.register('Source', Source)
    manager = BaseManager()
    manager.start()
    web_limit = cfg_parser.get_service_setting(SERVICE_NAME, "web_sources_limit", 5)
    tg_limit = cfg_parser.get_service_setting(SERVICE_NAME, "tg_sources_limit", 20)
    sources = [
        manager.Source(
            lib_web.BCSParser('https://bcs-express.ru/category/mirovye-rynki', 'BCS', web_limit),
            get_last_time('BCS'),
            'html'
        ),
        manager.Source(
            lib_web.FinamParser('https://www.finam.ru/analysis/nslent/', 'Finam', web_limit),
            get_last_time('Finam'),
            'html'
        ),
        manager.Source(
            lib_web.RBKParser('https://quote.rbc.ru/', 'RBK', web_limit),
            get_last_time('RBK'),
            'html'
        ),
        lib_parser.Source(
            lib_tg.TgParser('https://t.me/Full_Time_Trading', 'Full Time Trading', tg_limit),
            get_last_time('Full Time Trading'),
            'telegram'
        ),
        lib_parser.Source(
            lib_tg.TgParser('https://t.me/stock_and_news', 'Financial Times', tg_limit),
            get_last_time('Financial Times'),
            'telegram'
        ),
        lib_parser.Source(
            lib_tg.TgParser('https://t.me/mtwits', 'Market Twits', tg_limit),
            get_last_time('Market Twits'),
            'telegram'
        ),
    ]
    return sources


def get_news_from_source(source: lib_parser.Source) -> None:
    global telegram_timeout
    collected_news = []
    res = json.loads(source.get_parser().get_data())

    # TODO better logic
    if 'time_to_sleep' in res:
        telegram_timeout = int(time.time()) + int(res['time_to_sleep'])
        return

    last_time = source.get_last_time()
    for news in res:
        news_time = news['time']
        if source.get_last_time() is None or source.get_last_time() < news_time:
            collected_news.append(news)
        if last_time is None or last_time < news_time:
            last_time = news_time

    source.set_last_time(last_time)
    send(collected_news)


def send(data) -> None:
    for news in data:
        logger.info("%s, %s, %s" % (news['source'], news['time'], news['link']))
    resp = requests.post(FILTER_SERVICE_URL, json=data)
    if resp.status_code != 200:
        logger.critical(resp.text)


def main():
    sources = init_sources()
    workers = cfg_parser.get_service_setting(SERVICE_NAME, 'num_workers', 4)
    timeout = cfg_parser.get_service_setting(SERVICE_NAME, 'timeout', 1200)
    manager = BaseManager()
    manager.start()
    while True:
        pool = Pool(processes=workers)
        logger.info('Searching for news....')
        start_time = time.perf_counter()
        for source in sources:
            if source.get_type() != 'telegram':
                pool.apply_async(get_news_from_source, args=[source])
            else:
                # TODO better logic
                if int(time.time()) > telegram_timeout:
                    get_news_from_source(source)
        elapsed_time = time.perf_counter() - start_time
        pool.close()
        pool.join()
        logger.info(f"Elapsed time: {elapsed_time:0.4f} seconds")
        time.sleep(timeout)


if __name__ == '__main__':
    main()
