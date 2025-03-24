# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
from .omie_api import OmieApi

class OmieListAccountsReceivable:
    def __init__(self, company):
        self.company = company
        self.path = "finance/accounts_receivable/"
        self.call = "ListAccountsReceivable"
        self.page = 1
        self.records_per_page = 20
        self.only_imported_api = "N"

    def execute(self):
        return OmieApi().execute(self, self.company)

    def all(self):
        omie_list_name = "accounts_receivable_registration"
        self.records_per_page = 500
        query = self.execute()
        total_pages = query['total_pages']
        list_data = query[omie_list_name]
        while self.page < total_pages:
            self.page += 1
            records = self.execute()[omie_list_name]
            for record in records:
                list_data.append(record)
        return list_data
