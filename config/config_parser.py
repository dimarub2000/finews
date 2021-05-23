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

    def get_log_level(self, service, default_val) -> str:
        log_level = self.data.get(service, {}).get('log_level')
        if log_level is None:
            return default_val
        return log_level

    def get_log_format(self) -> str:
        log_format = self.data.get("common", {}).get('log_format')
        return log_format

    def get_date_format(self) -> str:
        date_format = self.data.get("common", {}).get('date_format')
        return date_format
