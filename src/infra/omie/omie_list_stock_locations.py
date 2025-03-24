# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
from .omie_api import OmieApi

class OmieListStockLocations:
    def __init__(self, company):
        self.company = company
        self.path = "stock/location/"
        self.call = 'ListStockLocations'
        self.page = 1
        self.records_per_page = 20

    def execute(self):
        return OmieApi().execute(self, self.company)
