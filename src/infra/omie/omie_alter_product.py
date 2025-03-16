from .omie_api import OmieApi

class OmieAlterProduct:
    def __init__(self, company):
        self.company = company
        self.path = "general/products/"
        self.call = "AlterProduct"
        self.product_code = 0

    def execute(self, console=True):
        return OmieApi().execute(self, self.company, console=console)
