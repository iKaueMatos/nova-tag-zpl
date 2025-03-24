# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
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
