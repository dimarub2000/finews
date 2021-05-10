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
SERVICE_NAME = 'parsers'

logging.basicConfig()
logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(cfg_parser.get_log_level(SERVICE_NAME, 'INFO'))


def init_sources() -> List:
    BaseManager.register('Source', Source)
    manager = BaseManager()
    manager.start()
    web_limit = cfg_parser.get_service_setting(SERVICE_NAME, "web_sources_limit", 5)
    tg_limit = cfg_parser.get_service_setting(SERVICE_NAME, "tg_sources_limit", 20)
    sources = [
        manager.Source(
            lib_web.BCSParser('https://bcs-express.ru/category/mirovye-rynki', web_limit),
            'BCS',
            None,
            'html'
        ),
        manager.Source(
            lib_web.FinamParser('https://www.finam.ru/analysis/nslent/', web_limit),
            'Finam',
            None,
            'html'
        ),
        manager.Source(
            lib_web.RBKParser('https://quote.rbc.ru/', web_limit),
            'RBK',
            None,
            'html'
        ),
        lib_parser.Source(
            lib_tg.TgParser('https://t.me/Full_Time_Trading', tg_limit),
            'Full Time Trading',
            None,
            'tg'
        ),
        lib_parser.Source(
            lib_tg.TgParser('https://t.me/stock_and_news', tg_limit),
            'Financial Times',
            None,
            'tg'
        ),
        lib_parser.Source(
            lib_tg.TgParser('https://t.me/mtwits', tg_limit),
            'Market Twits',
            None,
            'tg'
        ),
    ]
    return sources


def get_news_from_source(source: lib_parser.Source) -> None:
    collected_news = []
    res = json.loads(source.get_parser().get_data())
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
    timeout = cfg_parser.get_service_setting(SERVICE_NAME, 'timeout', 600)
    manager = BaseManager()
    manager.start()
    while True:
        pool = Pool(processes=workers)
        logger.info('Searching for news....')
        start_time = time.perf_counter()
        for source in sources:
            if source.get_type() != 'tg':
                pool.apply_async(get_news_from_source, args=[source])
            else:
                get_news_from_source(source)
        elapsed_time = time.perf_counter() - start_time
        pool.close()
        pool.join()
        logger.info(f"Elapsed time: {elapsed_time:0.4f} seconds")
        time.sleep(timeout)


if __name__ == '__main__':
    main()
