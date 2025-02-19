from zebra import Zebra

class ZebraPrinterService:
    def __init__(self, printer_name=None):
        self.z = Zebra()
        if printer_name:
            self.z.setqueue(printer_name)

    def get_printers(self):
        return self.z.getqueues()

    def set_printer(self, printer_name):
        self.z.setqueue(printer_name)

    def print_label(self, zpl_data):
        try:
            self.z.output(zpl_data)
            print("Etiqueta enviada para a impressora com sucesso!")
        except Exception as e:
            print("Erro ao imprimir:", str(e))