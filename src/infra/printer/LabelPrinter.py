import os
from sys import platform
from tkinter import messagebox


class LabelPrinter:
    def __init__(self, root):
        self.root = root

    def open_pdf(self, pdf_file):
        """
        Abre o PDF no visualizador do sistema operacional.
        :param pdf_file: Caminho do arquivo PDF.
        """
        system = platform.system()
        if system == "Windows":
            os.startfile(pdf_file)
        elif system == "Darwin":
            os.system(f"open {pdf_file}")
        else:
            os.system(f"xdg-open {pdf_file}")

        self.ask_for_print_confirmation(pdf_file)

    def ask_for_print_confirmation(self, pdf_file):
        """
        Pergunta ao usuário se deseja imprimir o PDF gerado.
        :param pdf_file: Caminho do arquivo PDF.
        """
        response = messagebox.askyesno("Imprimir PDF", "Deseja imprimir o PDF gerado?")

        if response:
            self.print_pdf(pdf_file)
        else:
            messagebox.showinfo("Cancelado", "Impressão cancelada!")

    def print_pdf(self, pdf_file):
        """
        Envia o PDF para a impressora.
        :param pdf_file: Caminho do arquivo PDF.
        """
        print(f"Enviando o PDF {pdf_file} para a impressora...")

        system = platform.system()
        if system == "Windows":
            os.startfile(pdf_file, "print")
        elif system == "Darwin":
            os.system(f"lp {pdf_file}")
        else:
            os.system(f"lp {pdf_file}")