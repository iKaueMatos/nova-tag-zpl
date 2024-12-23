class LabelGenerator:
    def generate_zpl(self, eans_and_skus, label_format):
        if label_format == "2-Colunas":
            return self._generate_zpl_2_columns(eans_and_skus)
        elif label_format == "1-Coluna":
            return self._generate_zpl_1_column(eans_and_skus)
        elif label_format == "4-etiquetas por página":
            return self._generate_zpl_4_labels_per_page(eans_and_skus)
        elif label_format == "Entiqueta Envio personalizado":
            return self._generate_zpl_custom_shipping(eans_and_skus)
        elif label_format == "QRCode":
            return self._generate_zpl_qrcode(eans_and_skus)
        elif label_format == "Code128":
            return self._generate_zpl_code128(eans_and_skus)
        else:
            raise ValueError("Formato de etiqueta desconhecido.")

    def _generate_zpl_2_columns(self, eans_and_skus):
        zpl = "^XA^CI28\n"
        x_offset = 0
        y_offset = 0
        label_width = 400
        label_height = 150
        max_columns = 2
        column_count = 0

        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                zpl += f"""
                ^LH{x_offset},{y_offset}
                ^FO65,10^BY3,,60^BEN,60,Y,N^FD{ean}^FS
                ^FO20,105^A0N,20,20^FDSKU: {sku}^FS
                """
                column_count += 1
                x_offset += label_width

                if column_count == max_columns:
                    x_offset = 0
                    y_offset += label_height
                    column_count = 0

        zpl += "^XZ"
        return zpl

    def _generate_zpl_1_column(self, eans_and_skus):
        zpl = "^XA^CI28\n"
        y_offset = 0
        label_height = 150

        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                zpl += f"""
                ^LH0,{y_offset}
                ^FO65,10^BY3,,60^BEN,60,Y,N^FD{ean}^FS
                ^FO20,105^A0N,20,20^FDSKU: {sku}^FS
                """
                y_offset += label_height

        zpl += "^XZ"
        return zpl

    def _generate_zpl_4_labels_per_page(self, data):
        zpl = "^XA^CI28\n"
        x_offset = 0
        y_offset = 0
        label_width = 400
        label_height = 150
        max_columns = 2
        max_rows = 2
        column_count = 0
        row_count = 0

        for ean, sku, quantity in data:
            for _ in range(quantity):
                zpl += f"""
                ^LH{x_offset},{y_offset}
                ^FO65,10^BY3,,60^BEN,60,Y,N^FD{ean}^FS
                ^FO20,105^A0N,20,20^FDSKU: {sku}^FS
                """
                column_count += 1
                x_offset += label_width

                if column_count == max_columns:
                    x_offset = 0
                    y_offset += label_height
                    column_count = 0
                    row_count += 1

                if row_count == max_rows:
                    x_offset = 0
                    y_offset = 0
                    row_count = 0

        zpl += "^XZ"
        return zpl

    def _generate_zpl_custom_shipping(self, eans_and_skus):
        zpl = "^XA^CI28\n"
        x_offset = 0
        y_offset = 0
        label_width = 600
        label_height = 300

        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                if not ean.isdigit():
                    raise ValueError("EAN deve conter apenas números.")
                zpl += f"""
                ^LH{x_offset},{y_offset}
                ^FO50,50^GB{label_width-100},{label_height-100},2^FS
                ^FO100,100^BY3,,60^BEN,60,Y,N^FD{ean}^FS
                """
                if sku:
                    zpl += f"""
                    ^FO100,200^A0N,30,30^FDSKU: {sku}^FS
                    """
                zpl += f"""
                ^FO100,250^A0N,30,30^FDQuantidade: {quantity}^FS
                """
                y_offset += label_height

        zpl += "^XZ"
        return zpl

    def _generate_zpl_qrcode(self, eans_and_skus):
        zpl = "^XA^CI28\n"
        y_offset = 0
        label_height = 150

        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                zpl += f"""
                ^LH0,{y_offset}
                ^FO50,50^BQN,2,10^FDQA,{ean}^FS
                """
                y_offset += label_height

        zpl += "^XZ"
        return zpl

    def _generate_zpl_code128(self, eans_and_skus):
        zpl = "^XA^CI28\n"
        y_offset = 0
        label_height = 150

        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                zpl += f"""
                ^LH0,{y_offset}
                ^FO50,50^BCN,100,Y,N,N^FD{ean}^FS
                """
                if sku:
                    zpl += f"""
                    ^FO50,160^A0N,30,30^FDSKU: {sku}^FS
                    """
                y_offset += label_height

        zpl += "^XZ"
        return zpl
