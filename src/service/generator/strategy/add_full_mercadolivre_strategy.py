from src.service.generator.strategy.add_strategy import AddStrategy

class AddFullMercadoLivreStrategy(AddStrategy):
    def add(self, generator, ean, sku, quantity, description, code, size):
        generator.add_sku_code_description_tag_full("", sku, quantity, description, code, size)