from .omie_api import OmieApi

class OmieConsultOrder:
    def __init__(self, company):
        self.company = company
        self.path = "products/order/"
        self.call = "ConsultOrder"
        self.order_code = 0

    def execute(self):
        return OmieApi().execute(self, self.company)
