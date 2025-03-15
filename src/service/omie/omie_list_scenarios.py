from .omie_api import OmieApi

class OmieListScenarios:
    def __init__(self, company):
        self.company = company
        self.path = "general/scenarios/"
        self.call = 'ListScenarios'
        self.page = 1
        self.records_per_page = 20

    def execute(self):
        return OmieApi().execute(self, self.company)
