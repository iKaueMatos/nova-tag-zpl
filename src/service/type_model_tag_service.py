class TypeModelTagService:
    def generate_ean(self, zpl: list, ean: str) -> None:
        zpl.append(f"^FO145,55^BY4,80,Y^BEN,100,Y^FD{ean}^FS")

    def generate_code_128(self, zpl: list, sku: str) -> None:
        zpl.append(f"^FO145,55^BY3,80,Y^BCN,100,Y^FD{sku}^FS")

    def append_both_label(self, zpl: list, ean: str, sku: str) -> None:
        zpl.append(f"^LH0,0\n^FO80,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
        zpl.append(f"^FO45,168^A0N,20,20^FDSKU: {sku}^FS")
        zpl.append(f"^FO475,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
        zpl.append(f"^FO440,168^A0N,20,20^FDSKU: {sku}^FS")