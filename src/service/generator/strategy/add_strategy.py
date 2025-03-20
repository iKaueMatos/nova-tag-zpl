from abc import ABC, abstractmethod

class AddStrategy(ABC):
    """Interface para a estratégia de adição de produtos."""

    @abstractmethod
    def add(self, generator, ean, sku, quantity, description, code, size):
        pass