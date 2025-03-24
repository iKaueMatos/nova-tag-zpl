# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
from .omie_api import OmieApi

class OmieListTaxScenarios:
    def __init__(self, company):
        self.company = company
        self.path = "general/scenarios/"
        self.call = 'ListTaxScenarios'
        self.final_consumption = "N"
        self.product_code = 0

    def execute(self):
        self.client_code_omie = OmieApi(self.company).client_tax()
        self.scenario_code = OmieApi(self.company).scenario_tax()
        return OmieApi().execute(self, self.company)