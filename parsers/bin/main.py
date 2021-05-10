import time
import json
import requests
import logging
import parsers.lib.parser as lib_parser
import parsers.lib.web as lib_web
import parsers.lib.telegram as lib_tg
from config.config_parser import FinewsConfigParser
from multiprocessing import Pool

from typing import List

cfg_parser = FinewsConfigParser()
FILTER_SERVICE_URL = cfg_parser.get_service_url('filter')
SERVICE_NAME = 'parsers'

logging.basicConfig()
logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(cfg_parser.get_log_level(SERVICE_NAME, 'INFO'))


def init_sources() -> List[lib_parser.Source]:
    sources = [
        lib_parser.Source(
            lib_web.BCSParser('https://bcs-express.ru/category/mirovye-rynki', 5),
            'BCS',
            None,
            'html'
        ),
        lib_parser.Source(
            lib_web.FinamParser('https://www.finam.ru/analysis/nslent/', 5),
            'Finam',
            None,
            'html'
        ),
        lib_parser.Source(
            lib_web.RBKParser('https://quote.rbc.ru/', 5),
            'RBK',
            None,
            'html'
        ),
        lib_parser.Source(
            lib_tg.TgParser('https://t.me/Full_Time_Trading', 10),
            'Full Time Trading',
            None,
            'tg'
        ),
        lib_parser.Source(
            lib_tg.TgParser('https://t.me/stock_and_news', 10),
            'Financial Times',
            None,
            'tg'
        ),
        lib_parser.Source(
            lib_tg.TgParser('https://t.me/mtwits', 10),
            'Market Twits',
            None,
            'tg'
        ),
    ]
    return sources


def get_news_from_source(source: lib_parser.Source) -> None:
    collected_news = []
    res = json.loads(source.parser.get_data())
    last_time = source.last_time
    for news in res:
        news_time = news['time']
        if source.last_time is None or source.last_time < news_time:
            collected_news.append(news)
        if last_time is None or last_time < news_time:
            last_time = news_time

    source.last_time = last_time
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
    while True:
        pool = Pool(processes=workers)
        logger.info('Searching for news....')
        start_time = time.perf_counter()
        for source in sources:
            if source.type != 'tg':
                pool.apply_async(get_news_from_source, args=(source,))
            else:
                get_news_from_source(source)
        elapsed_time = time.perf_counter() - start_time
        pool.close()
        pool.join()
        logger.info(f"Elapsed time: {elapsed_time:0.4f} seconds")
        time.sleep(timeout)


if __name__ == '__main__':
    main()
