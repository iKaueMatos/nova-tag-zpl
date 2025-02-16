from src.service.label_generator_service import LabelGenerator

class BarcodeLabelGenerator:
    def __init__(self):
        self.eans_and_skus = []
        self.label_format = "2-Colunas"
        self.quantity = 0
        self.label_generator = LabelGenerator()

    def add_ean_sku(self, ean, sku, quantity):
        self.eans_and_skus.append((ean, sku, quantity))

    def set_label_format(self, format_name):
        self.label_format = format_name

    def set_quantity(self, quantity):
        self.quantity = quantity

    def generate_zpl(self, label_format):
        return self.label_generator.generate_zpl(self.eans_and_skus, label_format)

    def save_zpl_to_file(self, zpl_code, file_path):
        with open(file_path, "w") as zpl_file:
            zpl_file.write(zpl_code)