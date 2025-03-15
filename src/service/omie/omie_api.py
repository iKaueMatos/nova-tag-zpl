import os
import requests
from dotenv import load_dotenv

class OmieApi:
    def __init__(self, company=""):
        self.path = ""
        self.call = ""
        load_dotenv()
        self.company = company

    def execute(self, method, company, console=False):
        self.company = company
        method_json = self._convert_to_json(method)
        params = method_json.copy()
        params.pop('path')
        params.pop('call')
        params.pop('company')

        json_data = {
            'app_key': self.key(),
            'app_secret': self.secret(),
            'call': method_json['call'],
            'param': [params]
        }
        response = requests.post(f'https://app.omie.com.br/api/v1/{method_json["path"]}', json=json_data)
        if console:
            print(response.json())
        return response.json()

    def _convert_to_json(self, method):
        old = method.__dict__
        class_name = method.__class__.__name__
        new = {}
        for attr in old:
            value = old[attr]
            attr = attr.replace(f"_{class_name}__", "").replace(f"_{class_name}_", "").replace(f"_{class_name}", "")
            new[attr] = value
        return new

    def key(self):
        return os.getenv(f'{self.company}_KEY')

    def secret(self):
        return os.getenv(f'{self.company}_SECRET')

    def client_tax(self):
        return os.getenv(f'{self.company}_CLIENT_TAX')

    def scenario_tax(self):
        return os.getenv(f'{self.company}_SCENARIO_TAX')

    def stock_location(self):
        return os.getenv(f'{self.company}_STOCK_LOCATION')
