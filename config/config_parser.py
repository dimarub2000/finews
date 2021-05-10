import json


class FinewsConfigParser(object):
    def __init__(self, file_path='config/config.json'):
        with open(file_path) as f:
            self.data = json.load(f)

    def get_service_url(self, service) -> str:
        return self.data[service]["addr"]

    def get_service_settings(self, service) -> dict:
        return self.data[service]["settings"]

    def get_service_setting(self, service, setting, default_val):
        val = self.get_service_settings(service).get(setting)
        if val is None:
            return default_val
        return val
