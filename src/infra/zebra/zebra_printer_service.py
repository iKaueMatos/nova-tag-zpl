from zebra import Zebra
import os

from src.utils.notification_windows_linux import NotificationWindowsLinux


class ZebraPrinterService:
    def __init__(self, printer_name=None):
        self.z = Zebra()
        self.density = 15
        if printer_name:
            self.z.setqueue(printer_name)

    def get_printers(self):
        return self.z.getqueues()

    def set_printer(self, printer_name):
        self.z.setqueue(printer_name)

    def print_label(self, zpl_data):
        try:
            self.z.output(zpl_data)
            NotificationWindowsLinux.show_notification("Sucesso", "Etiqueta enviada para a impressora com sucesso!")
        except Exception as e:
            error_message = f"Erro ao imprimir: {str(e)}"
            NotificationWindowsLinux.show_error_notification(error_message)

    def clear_print_queue(self):
        """Força a limpeza da fila de impressão no Windows."""
        try:
            print("Limpando a fila de impressão...")
            os.system("net stop spooler")
            os.system("del /Q /F C:\\Windows\\System32\\spool\\PRINTERS\\*")
            os.system("net start spooler")
            NotificationWindowsLinux.show_notification("Fila de Impressão Limpa", "Fila de impressão limpa com sucesso!")
            print("Fila de impressão limpa com sucesso!")
        except Exception as e:
            error_message = f"Erro ao limpar fila de impressão: {str(e)}"
            NotificationWindowsLinux.show_error_notification(error_message)
            print(error_message)

    def set_density(self, value):
        """Define a densidade de impressão. O valor pode ser entre 0 e 30."""
        if 0 <= value <= 30:
            self.density = value
            NotificationWindowsLinux.show_notification("Densidade Ajustada", f"Densidade de impressão ajustada para: {self.density}")
            print(f"Densidade de impressão ajustada para: {self.density}")
        else:
            error_message = "Valor de densidade inválido. A densidade deve estar entre 0 e 30."
            NotificationWindowsLinux.show_error_notification(error_message)
            print(error_message)