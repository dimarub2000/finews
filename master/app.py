import time
import os
import logging
import requests

from config.config_parser import FinewsConfigParser

cfg_parser = FinewsConfigParser()
SERVICE_NAME = 'master'
ADMINS = os.environ.get('ADMINS')
TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']

logging.basicConfig()
logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(cfg_parser.get_service_setting(SERVICE_NAME, 'log_level', 'INFO'))
logger.setFormatter(logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S"))


class Service(object):
    def __init__(self, service_url, service_name, path_to_logs, admins):
        self.service_url = service_url
        self.service_name = service_name
        self.path_to_logs = path_to_logs
        self.admins = admins

    def ping(self):
        try:
            resp = requests.get(self.service_url + '/ping')
            return resp.status_code
        except:
            return 500

    def get_traceback(self):
        try:
            with open(self.path_to_logs, 'r') as log:
                traceback = ""
                searching_for_trace = True
                for line in log:
                    if not searching_for_trace:
                        traceback += line
                    elif line == "Traceback (most recent call last):\n":
                        traceback += line
                        searching_for_trace = False
                return traceback
        except FileNotFoundError:
            return None

    def send_logs(self, status_code):
        if self.admins is None:
            logger.info("Admins is None")
            return
        for admin in self.admins:
            url = r'https://api.telegram.org/bot{}/{}'.format(TG_BOT_TOKEN, "sendMessage")
            log = "".join(["ALERT\n\n",
                           self.service_name,
                           " respond with status code: {}\n".format(status_code),
                           "Service Traceback:\n"])
            traceback = self.get_traceback()
            if traceback is None:
                logger.info("Cannot open logs file " + self.path_to_logs)
            else:
                log += traceback
            logger.info('Sending logs to %s' % admin)
            requests.post(url, data={"chat_id": admin, "text": log, "disable_web_page_preview": True})


def init_services(service_names):
    services = []
    if ADMINS is None:
        admins = None
    else:
        admins = ADMINS.split(",")
    for service in service_names:
        services.append(Service(cfg_parser.get_service_url(service),
                                service,
                                "".join([service, '/', service, '.err']),
                                admins))
        logger.info("watching service: " + service)
    return services


def ping_loop(services):
    timeout = cfg_parser.get_service_setting(SERVICE_NAME, "timeout", 600)
    while True:
        for service in services:
            logger.info("ping {}".format(service.service_name))
            status = service.ping()
            if status != 200:
                service.send_logs(status)
        time.sleep(timeout)


if __name__ == '__main__':
    time.sleep(60)
    ping_loop(init_services(["filter", "database", "search"]))
