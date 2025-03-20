from src.service.generator.strategy.add_strategy import AddStrategy

class AddEANStrategy(AddStrategy):
    def add(self, generator, ean, sku, quantity, description, code, size):
        generator.add_ean_sku(int(ean), sku, quantity, description)