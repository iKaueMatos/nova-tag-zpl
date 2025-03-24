# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
from src.service.generator.label_generator_service import LabelGenerator

class BarcodeLabelGenerator:
    def __init__(self):
        self.eans_and_skus = []
        self.label_format = "1-Coluna"
        self.model_tag = "EAN"
        self.label_generator = LabelGenerator(self.label_format, self.model_tag)

    def add_ean_sku(self, ean, sku, quantity, description):
        self.eans_and_skus.append((ean, sku, quantity, description))

    def add_sku_code_description_tag_full(self, ean, sku, quantity, description, code, size):
        self.eans_and_skus.append((ean, sku, quantity, description, code, size))
        print(self.eans_and_skus)

    def set_label_format(self, label_format, model_tag):
        self.label_format = label_format
        self.model_tag = model_tag
        self.label_generator = LabelGenerator(label_format, model_tag)

    def generate_zpl(self):
        return self.label_generator.generate_zpl(self.eans_and_skus, self.label_format, self.model_tag)