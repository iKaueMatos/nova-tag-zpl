import tkinter as tk
from tkinter import ttk

from src.utils.dialog_center import DialogCenter

class ShowShortcuts:
    @staticmethod
    def show_shortcuts(root):
        shortcuts = [
            ("Ctrl+P", "Selecionar Impressora"),
            ("Ctrl+A", "Selecionar Todos"),
            ("Ctrl+C", "Copiar Coluna"),
            ("Enter", "Gerar ZPL"),
            ("Double Click", "Editar Quantidade"),
        ]

        functionalities = [
            ("-Selecionar Impressora", "Permite selecionar a impressora para impressão."),
            ("-Importar Planilha", "Importa uma planilha com dados de EAN/SKU."),
            ("-Baixar Template", "Baixa um template de planilha."),
            ("-Gerar ZPL", "Gera o código ZPL para impressão."),
            ("-Imprimir", "Envia o código ZPL para a impressora."),
            ("-Salvar ZPL", "Salva o código ZPL em um arquivo."),
            ("-Limpar Dados", "Limpa todos os dados inseridos."),
            ("-Pausar Impressão", "Pausa a impressão cancelando a fila da impressora."),
            ("-Salvar Impressão", "Salva o código ZPL para impressão posterior."),
        ]

        popup = tk.Toplevel(root)
        popup.title("Atalhos e Funcionalidades")
        popup.geometry("600x400")
        popup.grab_set()

        DialogCenter.center_window(popup)

        tk.Label(popup, text="Atalhos Disponíveis", font=("Arial", 14, "bold")).pack(pady=10)
        for shortcut, description in shortcuts:
            tk.Label(popup, text=f"{shortcut}: {description}").pack(anchor="w", padx=20)

        tk.Label(popup, text="Funcionalidades", font=("Arial", 14, "bold")).pack(pady=10)
        for func, desc in functionalities:
            tk.Label(popup, text=f"{func}: {desc}").pack(anchor="w", padx=20)

        ttk.Button(popup, text="Fechar", command=popup.destroy).pack(pady=10)