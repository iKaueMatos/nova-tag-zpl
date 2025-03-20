from src.service.generator.strategy.add_strategy import AddStrategy

class AddSKUStrategy(AddStrategy):
    def add(self, generator, ean, sku, quantity, description, code, size):
        generator.add_ean_sku("", sku, quantity, description)