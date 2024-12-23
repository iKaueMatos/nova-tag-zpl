import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from src.models.barcode_label_generator import BarcodeLabelGenerator

class BarcodeLabelApp:
    def __init__(self, root):
        self.generator = BarcodeLabelGenerator()
        self.root = root

        self.root = root
        self.root.title("Gerador de Etiquetas - ZPL")
        
        self.frame = ttk.Frame(root, padding=10)
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(self.frame, text="EAN:").grid(row=0, column=0, sticky=tk.W)
        self.ean_entry = ttk.Entry(self.frame, width=30)
        self.ean_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Label(self.frame, text="SKU:").grid(row=1, column=0, sticky=tk.W)
        self.sku_entry = ttk.Entry(self.frame, width=30)
        self.sku_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Label(self.frame, text="Quantidade:").grid(row=2, column=0, sticky=tk.W)
        self.quantity_entry = ttk.Entry(self.frame, width=10)
        self.quantity_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

        self.add_button = ttk.Button(self.frame, text="Adicionar", command=self.add_entry)
        self.add_button.grid(row=2, column=2, sticky=tk.E)

        self.tree = ttk.Treeview(self.frame, columns=("EAN", "SKU", "Quantidade"), show="headings")
        self.tree.heading("EAN", text="EAN")
        self.tree.heading("SKU", text="SKU")
        self.tree.heading("Quantidade", text="Quantidade")
        self.tree.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))

        self.import_button = ttk.Button(self.frame, text="Importar Planilha", command=self.import_sheet)
        self.import_button.grid(row=4, column=0, sticky=tk.W)

        self.generate_button = ttk.Button(self.frame, text="Gerar ZPL", command=self.generate_zpl)
        self.generate_button.grid(row=4, column=1, sticky=tk.W)

        self.save_button = ttk.Button(self.frame, text="Salvar ZPL", command=self.save_zpl)
        self.save_button.grid(row=4, column=2, sticky=tk.E)

        ttk.Label(self.frame, text="Formato da Etiqueta:").grid(row=5, column=0, sticky=tk.W)
        self.label_format = tk.StringVar(value="2-Colunas")
        self.format_combobox = ttk.Combobox(self.frame, textvariable=self.label_format, state="readonly")
        self.format_combobox['values'] = ("2-Colunas", "1-Coluna", "4-etiquetas por página", "Etiqueta Envio personalizado", "QRCode", "Code128")
        self.format_combobox.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E))
        self.format_combobox.current(0)  # Set default value

        self.root.bind('<Return>', lambda event: self.generate_zpl())
        
    def add_entry(self):
        ean = self.ean_entry.get().strip()
        sku = self.sku_entry.get().strip()
        quantity = self.quantity_entry.get().strip()

        if not ean or not sku or not quantity.isdigit():
            messagebox.showerror("Erro", "Por favor, preencha todos os campos corretamente.")
            return

        if not self.generator.validate_ean(ean):
            messagebox.showerror("Erro", "EAN inválido. Verifique o código.")
            return

        self.generator.add_ean_sku(ean, sku, int(quantity))
        self.tree.insert("", tk.END, values=(ean, sku, quantity))

        self.ean_entry.delete(0, tk.END)
        self.sku_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)

    def import_sheet(self):
        file_path = filedialog.askopenfilename(filetypes=[("Planilhas", "*.csv *.xlsx")])
        if not file_path:
            return

        try:
            if file_path.endswith(".csv"):
                data = pd.read_csv(file_path)
            else:
                data = pd.read_excel(file_path)

            for _, row in data.iterrows():
                ean = str(row.get("EAN", "")).strip()
                sku = str(row.get("SKU", "")).strip()
                quantity = int(row.get("Quantidade", 0))

                if not self.generator.validate_ean(ean):
                    continue

                self.generator.add_ean_sku(ean, sku, quantity)
                self.tree.insert("", tk.END, values=(ean, sku, quantity))

            messagebox.showinfo("Sucesso", "Dados importados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar planilha: {e}")

    def generate_zpl(self):
        if not self.generator.eans_and_skus:
            messagebox.showerror("Erro", "Nenhum dado para gerar etiqueta. Adicione EANs e SKUs primeiro.")
            return

        self.generator.set_label_format(self.label_format.get())
        zpl_code = self.generator.generate_zpl()
        messagebox.showinfo("Sucesso", "Código ZPL gerado com sucesso!")
        print("ZPL Code:", zpl_code)

    def save_zpl(self):
        if not self.generator.eans_and_skus:
            messagebox.showerror("Erro", "Nenhum dado para salvar etiqueta. Adicione EANs e SKUs primeiro.")
            return

        zpl_code = self.generator.generate_zpl()
        file_path = filedialog.asksaveasfilename(defaultextension=".zpl",
                                                 filetypes=[("Arquivo ZPL", "*.zpl")])
        if file_path:
            self.generator.save_zpl_to_file(zpl_code, file_path)
            messagebox.showinfo("Sucesso", f"Arquivo salvo em: {file_path}")

    def print_zpl(self):
        if not self.generator.eans_and_skus:
            messagebox.showerror("Erro", "Nenhum dado para imprimir etiqueta. Adicione EANs e SKUs primeiro.")
            return

        zpl_code = self.generator.generate_zpl()
        self.generator.print_zpl(zpl_code)
        messagebox.showinfo("Sucesso", "Etiqueta enviada para a impressora.")