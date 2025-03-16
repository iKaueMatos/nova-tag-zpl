from .omie_api import OmieApi

class OmieListAttachments:
    def __init__(self, company):
        self.company = company
        self.path = "general/attachments/"
        self.call = "ListAttachments"
        self.page = 1
        self.records_per_page = 500
        self.id = 0
        self.table = ""

    def execute(self, console=False):
        return OmieApi().execute(self, self.company, console=console)
