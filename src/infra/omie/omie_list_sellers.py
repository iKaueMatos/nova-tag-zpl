from .omie_api import OmieApi

class OmieListSellers:
    def __init__(self, company):
        self.company = company
        self.path = "general/sellers/"
        self.call = "ListSellers"
        self.page = "1"
        self.records_per_page = 100
        self.only_imported_api = "N"

    def execute(self, console=False):
        return OmieApi().execute(self, self.company, console=console)
