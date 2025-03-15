import os
import sqlite3

import requests
from datetime import date
from dotenv import load_dotenv
from .omie_alter_price_item import OmieAlterPriceItem
from .omie_alter_product import OmieAlterProduct
from .omie_consult_client import OmieConsultClient
from .omie_consult_order import OmieConsultOrder
from .omie_consult_seller import OmieConsultSeller
from .omie_list_scenarios import OmieListScenarios
from .omie_list_clients import OmieListClients
from .omie_list_accounts_payable import OmieListAccountsPayable
from .omie_list_accounts_receivable import OmieListAccountsReceivable
from .omie_list_attachments import OmieListAttachments
from .omie_list_tax_scenarios import OmieListTaxScenarios
from .omie_list_stock_locations import OmieListStockLocations
from .omie_list_orders import OmieListOrders
from .omie_list_stock_positions import OmieListStockPositions
from .omie_list_products import OmieListProducts
from .omie_list_price_table_items import OmieListPriceTableItems
from .omie_list_price_tables import OmieListPriceTables
from .omie_list_sellers import OmieListSellers
from .omie_get_attachment import OmieGetAttachment
from ...core.database.repositories.credentials_repo import CredentialsRepository


class Omie:
    def __init__(self, company):
        self.AlterPriceItem = OmieAlterPriceItem(company)
        self.AlterProduct = OmieAlterProduct(company)
        self.ConsultClient = OmieConsultClient(company)
        self.ConsultOrder = OmieConsultOrder(company)
        self.ConsultSeller = OmieConsultSeller(company)
        self.ListScenarios = OmieListScenarios(company)
        self.ListClients = OmieListClients(company)
        self.ListAccountsPayable = OmieListAccountsPayable(company)
        self.ListAccountsReceivable = OmieListAccountsReceivable(company)
        self.ListAttachments = OmieListAttachments(company)
        self.ListTaxScenarios = OmieListTaxScenarios(company)
        self.ListStockLocations = OmieListStockLocations(company)
        self.ListOrders = OmieListOrders(company)
        self.ListStockPositions = OmieListStockPositions(company)
        self.ListProducts = OmieListProducts(company)
        self.ListPriceTableItems = OmieListPriceTableItems(company)
        self.ListPriceTables = OmieListPriceTables(company)
        self.ListSellers = OmieListSellers(company)
        self.GetAttachment = OmieGetAttachment(company)

class OmieApi:
    def __init__(self, company=""):
        self.company = company
        self.credentials = CredentialsRepository.get_credentials(company)

    def key(self):
        return self.credentials["app_key"] if self.credentials else None

    def secret(self):
        return self.credentials["app_secret"] if self.credentials else None

    def client_tax(self):
        return self.credentials["client_tax"] if self.credentials else None

    def tax_scenario(self):
        return self.credentials["tax_scenario"] if self.credentials else None

    def stock_location(self):
        return self.credentials["stock_location"] if self.credentials else None

    def execute(self, method, company, console=False):
        self.company = company
        self.credentials = CredentialsRepository.get_credentials(company)

        method_json = self._convert_json(method)

        params = method_json.copy()
        params.pop("caminho", None)
        params.pop("call", None)
        params.pop("empresa", None)

        json_data = {
            "app_key": self.key(),
            "app_secret": self.secret(),
            "call": method_json["call"],
            "param": [params]
        }

        response = requests.post(f"https://app.omie.com.br/api/v1/{method_json['caminho']}", json=json_data)

        if console:
            print(response.json())

        return response.json()

    def _convert_json(self, method):
        old_dict = method.__dict__
        class_name = method.__class__.__name__
        new_dict = {}

        for attribute in old_dict:
            value = old_dict[attribute]
            attribute = attribute.replace(f"_{class_name}__", "").replace(f"_{class_name}_", "").replace(
                f"_{class_name}", "")
            new_dict[attribute] = value

        return new_dict