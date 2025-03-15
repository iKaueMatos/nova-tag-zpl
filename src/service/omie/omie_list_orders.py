from .omie_api import OmieApi

class OmieListOrders:
    def __init__(self, company):
        self.company = company
        self.path = "products/order/"
        self.call = "ListOrders"
        self.page = 1
        self.records_per_page = 100
        self.only_imported_api = "N"

    def execute(self, console=False):
        return OmieApi().execute(self, self.company, console=console)

    def all(self, console=False):
        omie_list_name = "order_sale_product"
        self.records_per_page = 500
        query = self.execute(console=console)
        total_pages = query['total_pages']
        list_data = query[omie_list_name]
        while self.page < total_pages:
            self.page += 1
            page_list = self.execute(console=console)[omie_list_name]
            for item in page_list:
                list_data.append(item)
        return list_data
