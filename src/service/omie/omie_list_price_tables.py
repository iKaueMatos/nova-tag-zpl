from .omie_api import OmieApi

class OmieListPriceTables:
    def __init__(self, company):
        self.company = company
        self.path = "products/price_table/"
        self.call = 'ListPriceTables'
        self.page = 1
        self.records_per_page = 20

    def execute(self, console=False):
        return OmieApi().execute(self, self.company, console=console)
