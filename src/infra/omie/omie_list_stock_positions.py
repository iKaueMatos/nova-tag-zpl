# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
from .omie_api import OmieApi

class OmieListStockPositions:
    def __init__(self, company):
        self.company = company
        self.path = "stock/consult/"
        self.call = 'ListStockPositions'
        self.page = 1
        self.records_per_page = 20
        self.position_date = date.today().strftime("%d/%m/%Y")
        self.show_all = "N"
        self.stock_location_code = OmieApi(company).stock_location()

    def execute(self, console=False):
        return OmieApi().execute(self, self.company, console=console)

    def all(self, console=False):
        omie_list_name = "products"
        self.records_per_page = 500
        query = self.execute(console=console)
        total_pages = query['total_pages']
        list_data = query[omie_list_name]
        while self.page < total_pages:
            self.page += 1
            products = self.execute()[omie_list_name]
            for product in products:
                list_data.append(product)
        return list_data
