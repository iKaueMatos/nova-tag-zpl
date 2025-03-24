# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
from .omie_api import OmieApi

class OmieConsultClient:
    def __init__(self, company):
        self.company = company
        self.path = "general/clients/"
        self.call = "ConsultClient"
        self.client_code_omie = 0
        self.client_code_integration = ""

    def execute(self):
        return OmieApi().execute(self, self.company)
