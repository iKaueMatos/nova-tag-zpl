from .omie_api import OmieApi

class OmieListPriceTableItems:
    def __init__(self, company):
        self.company = company
        self.path = "products/price_table/"
        self.call = 'ListPriceTableItems'
        self.page = 1
        self.records_per_page = 20
        self.price_table_code = 0

    def execute(self, console=False):
        return OmieApi().execute(self, self.company, console=console)

    def all(self, console=False):
        omie_list_name = "price_table_list"
        self.records_per_page = 500
        query = self.execute()
        total_pages = query['total_pages']
        list_data = query[omie_list_name]['table_items']
        while self.page < total_pages:
            self.page += 1
            search = self.execute(console=console)
            products = search[omie_list_name]['table_items']
            for product in products:
                list_data.append(product)
        return list_data
