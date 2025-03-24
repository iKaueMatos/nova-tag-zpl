# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
from src.service.generator.strategy.add_strategy import AddStrategy

class AddFullAmazonStrategy(AddStrategy):
    def add(self, generator, ean, sku, quantity, description, code, size):
        generator.add_sku_code_description_tag_full("", sku, quantity, description, code, "")