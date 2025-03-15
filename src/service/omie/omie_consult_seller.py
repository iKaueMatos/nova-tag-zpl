from .omie_api import OmieApi

class OmieConsultSeller:
    def __init__(self, company):
        self.company = company
        self.path = "general/sellers/"
        self.call = "ConsultSeller"
        self.code = 0
        self.integration_code = ""

    def execute(self):
        return OmieApi().execute(self, self.company)
