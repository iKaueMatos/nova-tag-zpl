from .omie_api import OmieApi

class OmieListClients:
    def __init__(self, company):
        self.company = company
        self.path = "general/clients/"
        self.call = 'ListClients'
        self.page = 1
        self.records_per_page = 50

    def execute(self):
        return OmieApi().execute(self, self.company)

    def all(self):
        omie_list_name = "clients_registration"
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
