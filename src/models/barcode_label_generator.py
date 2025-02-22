from src.service.label_generator_service import LabelGenerator

class BarcodeLabelGenerator:
    def __init__(self, label_format="1-Coluna"):
        self.eans_and_skus = []
        self.quantity = 0
        self.label_format = label_format
        self.label_generator = LabelGenerator(label_format)

    def add_ean_sku(self, ean, sku, quantity):
        self.eans_and_skus.append((ean, sku, quantity))

    def set_label_format(self, format_name):
        self.label_format = format_name
        self.label_generator.label_format = format_name

    def set_quantity(self, quantity):
        self.quantity = quantity

    def generate_zpl(self, label_format=None):
        return self.label_generator.generate_zpl(self.eans_and_skus, label_format or self.label_format)

    def save_zpl_to_file(self, zpl_code, file_path):
        with open(file_path, "w") as zpl_file:
            zpl_file.write(zpl_code)