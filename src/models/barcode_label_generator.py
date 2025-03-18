from src.service.generator.label_generator_service import LabelGenerator

class BarcodeLabelGenerator:
    def __init__(self):
        self.eans_and_skus = []
        self.label_format = "1-Coluna"
        self.label_generator = LabelGenerator(self.label_format)

    def add_ean_sku(self, ean, sku, quantity, description):
        self.eans_and_skus.append((ean, sku, quantity, description))

    def set_label_format(self, label_format):
        self.label_format = label_format
        self.label_generator = LabelGenerator(label_format)

    def generate_zpl(self):
        return self.label_generator.generate_zpl(self.eans_and_skus, self.label_format)