
class LabelItem:
    def __init__(self, ean: str, sku: str, quantity: int, description: str, code: str, size: str, **kwargs):
        self.ean = ean
        self.sku = sku
        self.quantity = quantity
        self.description = description
        self.code = code
        self.size = size

        for key, value in kwargs.items():
            setattr(self, key, value)