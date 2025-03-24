# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
from src.service.generator.strategy.add_strategy import AddStrategy

class AddBothStrategy(AddStrategy):
    def add(self, generator, ean, sku, quantity, description, code, size):
        generator.add_ean_sku(int(ean), sku, int(quantity), description)