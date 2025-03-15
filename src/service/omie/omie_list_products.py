from .omie_api import OmieApi

class OmieListProducts:
    def __init__(self, company):
        self.company = company
        self.path = "general/products/"
        self.call = 'ListProducts'
        self.page = 1
        self.records_per_page = 50
        self.only_imported_api = 'N'
        self.filter_only_omiepdv = 'N'

    def execute(self, console=False):
        return OmieApi().execute(self, self.company, console=console)

    def all(self, console=False):
        omie_list_name = "product_service_registration"
        self.records_per_page = 500
        query = self.execute(console=console)
        total_pages = query['total_pages']
        list_data = query[omie_list_name]
        while self.page < total_pages:
            self.page += 1
            products = self.execute(console=console)[omie_list_name]
            for product in products:
                list_data.append(product)
        return list_data
