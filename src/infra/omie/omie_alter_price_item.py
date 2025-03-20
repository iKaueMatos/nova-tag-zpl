# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
from .omie_api import OmieApi

class OmieAlterPriceItem:
    def __init__(self, company):
        self.company = company
        self.path = "products/price_table/"
        self.call = "AlterPriceItem"
        self.price_table_code = 0
        self.product_code = 0
        self.price_value = 0

    def execute(self, console=True):
        return OmieApi().execute(self, self.company, console=console)
