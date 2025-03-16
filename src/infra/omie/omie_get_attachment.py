from .omie_api import OmieApi

class OmieGetAttachment:
    def __init__(self, company):
        self.company = company
        self.path = "general/attachments/"
        self.call = "GetAttachment"
        self.attachment_code = "",
        self.table = "",
        self.id = 0,
        self.attachment_id = 0,
        self.file_name = ""

    def execute(self, console=False):
        return OmieApi().execute(self, self.company, console=console)
