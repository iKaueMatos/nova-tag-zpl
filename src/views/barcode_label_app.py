import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext
import pandas as pd
import math
import requests
import io
from PIL import Image, ImageTk

from src.enum.LabelFormatConstants import LabelFormatConstants
from src.models.barcode_label_generator import BarcodeLabelGenerator
from src.service.sheet_importer import SheetImporter
from src.service.zebra_labelary_api_service import ZebraLabelaryApiService
from src.service.zebra_printer_service import ZebraPrinterService

class BarcodeLabelApp:
    def __init__(self, root):
        self.generator = BarcodeLabelGenerator()
        self.printer_service = ZebraPrinterService()
        self.zpl_code = None
        self.selected_printer = None
        self.zebra_laberaly_api_service = ZebraLabelaryApiService()
        self.root = root

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        left_frame = ttk.Frame(root, padding=20)
        left_frame.grid(row=0, column=0, sticky="nsew")

        self.right_frame = ttk.Frame(root, padding=20)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # ----------------- Lado Esquerdo: Controles de Geração e Gerenciamento do ZPL -----------------
        # ----------------- Linha 0: Tipo de Código -----------------
        ttk.Label(left_frame, text="Tipo de Código:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.code_type = tk.StringVar(value="EAN")
        self.code_type_combobox = ttk.Combobox(left_frame, textvariable=self.code_type, state="readonly")
        self.code_type_combobox['values'] = ("EAN", "SKU", "QRCode", "Code128", "Ambos")
        self.code_type_combobox.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.code_type_combobox.bind("<<ComboboxSelected>>", self.toggle_fields)

        # ----------------- Linha 1: EAN -----------------
        ttk.Label(left_frame, text="EAN:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ean_entry = ttk.Entry(left_frame)
        self.ean_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # ----------------- Linha 2: SKU -----------------
        ttk.Label(left_frame, text="SKU:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.sku_entry = ttk.Entry(left_frame)
        self.sku_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # ----------------- Linha 3: Quantidade e Botão Adicionar -----------------
        ttk.Label(left_frame, text="Quantidade:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.quantity_entry = ttk.Entry(left_frame, width=10)
        self.quantity_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.add_button = ttk.Button(left_frame, text="Adicionar", command=self.add_entry)
        self.add_button.grid(row=3, column=2, sticky="e", padx=5, pady=5)

        # ----------------- Linha 4: TreeView -----------------
        tree_frame = ttk.Frame(left_frame)
        tree_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=("EAN", "SKU", "Quantidade"), show="headings", height=8)
        self.tree.heading("EAN", text="EAN")
        self.tree.heading("SKU", text="SKU")
        self.tree.heading("Quantidade", text="Quantidade")

        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(expand=True, fill="both")

        left_frame.rowconfigure(4, weight=1)

        # ----------------- Linha 5: Rótulo para o ZPL -----------------
        ttk.Label(left_frame, text="Código ZPL Gerado:").grid(row=5, column=0, columnspan=3, sticky="w", padx=5, pady=5)

        # ----------------- Linha 6: Área de Texto (desabilitada) -----------------
        self.label_text = scrolledtext.ScrolledText(left_frame, width=50, height=10, state=tk.DISABLED)
        self.label_text.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        left_frame.rowconfigure(6, weight=1)

        # ----------------- Linha 7: Botões de Ação (linha 1) -----------------
        button_frame1 = ttk.Frame(left_frame)
        button_frame1.grid(row=7, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        button_frame1.columnconfigure(0, weight=1)
        button_frame1.columnconfigure(1, weight=1)
        button_frame1.columnconfigure(2, weight=1)

        self.importer = SheetImporter(self.generator, self.tree, self.code_type)
        self.import_button = ttk.Button(button_frame1, text="Importar Planilha", command=self.import_sheet)
        self.import_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.generate_button = ttk.Button(button_frame1, text="Gerar ZPL", command=self.generate_zpl)
        self.generate_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.clear_button = ttk.Button(button_frame1, text="Limpar Dados", command=self.clear_data)
        self.clear_button.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        # ----------------- Linha 8: Botões de Ação (linha 2) -----------------
        button_frame2 = ttk.Frame(left_frame)
        button_frame2.grid(row=8, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        button_frame2.columnconfigure(0, weight=1)
        button_frame2.columnconfigure(1, weight=1)
        button_frame2.columnconfigure(2, weight=1)
        self.select_printer_button = ttk.Button(button_frame2, text="Selecionar Impressora",
                                                command=self.select_printer, state=tk.DISABLED)
        self.select_printer_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.print_button = ttk.Button(button_frame2, text="Imprimir",
                                       command=self.print_label, state=tk.DISABLED)

        self.print_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.download_button = ttk.Button(button_frame2, text="Baixar Template", command=self.download_template)
        self.download_button.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        self.save_button = ttk.Button(button_frame2, text="Salvar ZPL", command=self.save_zpl)
        self.save_button.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        # ----------------- Linha 9: Formato da Etiqueta -----------------
        ttk.Label(left_frame, text="Formato da Etiqueta:").grid(row=9, column=0, sticky="w", padx=5, pady=5)
        self.label_format = tk.StringVar(value="2-Colunas")
        self.format_combobox = ttk.Combobox(left_frame, textvariable=self.label_format, state="readonly")
        self.format_combobox['values'] = ("2-Colunas", "1-Coluna")
        self.format_combobox.grid(row=9, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # ----------------- Lado Direito: Imagem e Pré-visualização -----------------
        self.preview_label = ttk.Label(self.right_frame, text="Imagem da Etiqueta")
        self.preview_label.grid(row=0, column=0, pady=10)

        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        preview_frame = ttk.LabelFrame(self.right_frame, text="Pré-visualização da Etiqueta")
        preview_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.right_frame.rowconfigure(0, weight=1)
        self.right_frame.columnconfigure(0, weight=1)

        preview_frame.config(width=600, height=400)

        self.preview_image_label = ttk.Label(preview_frame)
        self.preview_image_label.pack(expand=True, fill="both", padx=5, pady=5)

        self.update_preview_button = ttk.Button(self.right_frame, text="Atualizar Preview", command=self.update_preview)
        self.update_preview_button.grid(row=1, column=0, pady=10)

        self.root.bind('<Return>', lambda event: self.generate_zpl())
        self.toggle_fields()

    def update_preview(self):
        """
            Gera a imagem a partir do ZPL (via Labelary) e exibe no Label de preview.
        """
        if not self.zpl_code:
            messagebox.showerror("Erro", "Nenhum código ZPL para pré-visualizar.")
            return

        selected_label_format = self.label_format.get()

        if selected_label_format is None:
            messagebox.showerror("Erro", "Selecione um formato de etiqueta.")
            return

        def get_first_zpl_block(zpl_code):
            if "^XZ" in zpl_code:
                first_block = zpl_code.split("^XZ")[0] + "^XZ"
                return first_block
            return None

        zpl_code_to_send = get_first_zpl_block(self.zpl_code)

        if not zpl_code_to_send:
            messagebox.showerror("Erro", "Código ZPL inválido ou não encontrado.")
            return

        printer_density = LabelFormatConstants.PRINTER_DENSITY_8DPMM
        label_dimensions = LabelFormatConstants.LABEL_DIMENSIONS_5X25
        label_index = LabelFormatConstants.LABEL_INDEX_0
        output_format = LabelFormatConstants.OUTPUT_FORMAT_IMAGE

        image = self.zebra_laberaly_api_service.generate_preview_image(
            zpl_code_to_send,
            printer_density,
            label_dimensions,
            label_index,
            output_format
        )

        if image:
            width, height = image.size
            new_width = 800
            new_height = int((new_width / width) * height)
            image = image.resize((new_width, new_height), Image.LANCZOS)

            self.preview_image_tk = ImageTk.PhotoImage(image)
            self.preview_image_label.config(image=self.preview_image_tk)
            self.preview_image_label.image = self.preview_image_tk
        else:
            messagebox.showerror("Erro", "Falha ao gerar a pré-visualização da etiqueta.")

    def select_printer(self):
        printers = self.printer_service.get_printers()
        if not printers:
            messagebox.showerror("Erro", "Nenhuma impressora disponível.")
            return

        printer_name = simpledialog.askstring("Selecionar Impressora", "Escolha uma impressora:",
                                              initialvalue=printers[0])
        if printer_name and printer_name in printers:
            self.selected_printer = printer_name
            self.printer_service.set_printer(printer_name)
            messagebox.showinfo("Sucesso", f"Impressora selecionada: {printer_name}")
        else:
            messagebox.showwarning("Aviso", "Nenhuma impressora selecionada.")

    def print_label(self):
        if not self.selected_printer:
            messagebox.showerror("Erro", "Selecione uma impressora antes de imprimir.")
            return

        zpl_data = self.label_text.get("1.0", tk.END).strip()
        if not zpl_data:
            messagebox.showerror("Erro", "Nenhum código ZPL para imprimir.")
            return

        self.printer_service.print_label(zpl_data)
        messagebox.showinfo("Sucesso", "Etiqueta enviada para a impressora.")

    def toggle_fields(self, event=None):
        if self.code_type.get() == "EAN":
            self.ean_entry.config(state="normal")
            self.sku_entry.config(state="disabled")
        elif self.code_type.get() == "SKU":
            self.sku_entry.config(state="normal")
            self.ean_entry.config(state="disabled")
        elif self.code_type.get() == "Ambos":
            self.ean_entry.config(state="normal")
            self.sku_entry.config(state="normal")
        elif self.code_type.get() == "Code128":
            self.ean_entry.config(state="disabled")
            self.sku_entry.config(state="normal")
        elif self.code_type.get() == "EAN":
            self.ean_entry.config(state="disabled")
            self.sku_entry.config(state="normal")
        elif self.code_type.get() == "QRCode":
            self.ean_entry.config(state="disabled")
            self.sku_entry.config(state="normal")

    def clear_data(self):
        if self.tree.get_children():
            self.tree.delete(*self.tree.get_children())
            self.generator.eans_and_skus.clear()
            messagebox.showinfo("Sucesso", "Todos os dados foram limpos.")
        else:
            messagebox.showinfo("Informação", "Nenhum dado para limpar.")

    def add_entry(self):
        ean = self.ean_entry.get().strip()
        sku = self.sku_entry.get().strip()
        quantity = self.quantity_entry.get().strip()

        if not quantity.isdigit():
            messagebox.showerror("Erro", "Quantidade inválida.")
            return

        if self.code_type.get() == "EAN" and not ean:
            messagebox.showerror("Erro", "Por favor, preencha o campo EAN.")
            return
        if self.code_type.get() == "SKU" and not sku:
            messagebox.showerror("Erro", "Por favor, preencha o campo SKU.")
            return

        if self.code_type.get() == "EAN":
            self.generator.add_ean_sku(int(ean), "", int(quantity))
        if self.code_type.get() == "SKU":
            self.generator.add_ean_sku("", sku, int(quantity))
        if self.code_type.get() == "Ambos":
            self.generator.add_ean_sku(int(ean), sku, int(quantity))

        item_id = self.tree.insert("", tk.END, values=(ean, sku, quantity))

        self.ean_entry.delete(0, tk.END)
        self.sku_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)

    def calculate_quantity_to_send(self, total_quantity, columns):
        if columns == 2:
            return total_quantity if total_quantity % 2 == 0 else total_quantity + 1
        elif columns == 4:
            return math.ceil(total_quantity / 4) * 4
        return total_quantity

    def download_template(self):
        def on_select_template_type():
            selected_type = self.template_type.get()
            template_data = pd.DataFrame()

            if selected_type == "EAN":
                template_data = pd.DataFrame({
                    "EAN": ["", "", ""],
                    "Quantidade": [0, 0, 0]
                })
            elif selected_type == "SKU":
                template_data = pd.DataFrame({
                    "SKU": ["", "", ""],
                    "Quantidade": [0, 0, 0]
                })
            elif selected_type == "Ambos":
                template_data = pd.DataFrame({
                    "EAN": ["", "", ""],
                    "SKU": ["", "", ""],
                    "Quantidade": [0, 0, 0]
                })

            file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                     filetypes=[("CSV", "*.csv")])
            if file_path:
                try:
                    template_data.to_csv(file_path, index=False)
                    messagebox.showinfo("Sucesso", f"Template salvo em: {file_path}")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao salvar o template: {e}")
            dialog.destroy()

        dialog = tk.Toplevel(self.root)
        dialog.title("Escolha o tipo de Planilha")

        ttk.Label(dialog, text="Selecione o tipo de planilha que deseja gerar:") \
            .grid(row=0, column=0, pady=10, padx=10)

        self.template_type = tk.StringVar(value="EAN")
        type_combobox = ttk.Combobox(dialog, textvariable=self.template_type, state="readonly")
        type_combobox['values'] = ("EAN", "SKU", "Ambos")
        type_combobox.grid(row=1, column=0, pady=10, padx=10)

        generate_button = ttk.Button(dialog, text="Gerar Template", command=on_select_template_type)
        generate_button.grid(row=2, column=0, pady=10, padx=10)

        dialog.grab_set()
        dialog.mainloop()

    def import_sheet(self):
        self.importer.import_sheet()

    def generate_zpl(self):
        selected_items = self.tree.selection()

        if not selected_items:
            messagebox.showerror("Erro", "Por favor, selecione ao menos uma linha na tabela.")
            return

        selected_type = self.code_type.get()
        labels_data = []

        for item in selected_items:
            item_values = self.tree.item(item, 'values')

            ean, sku, quantity_str = item_values

            if not quantity_str.isdigit():
                messagebox.showwarning("Aviso", f"Quantidade inválida na linha: {item_values}. Ignorando.")
                continue

            quantity = int(quantity_str)

            if selected_type == "EAN" and not ean:
                continue
            if selected_type == "SKU" and not sku:
                continue

            label_format = self.label_format.get()
            columns = 1

            if label_format == "2-Colunas":
                columns = 2
            elif label_format == "4-etiquetas por página":
                columns = 4

            adjusted_quantity = self.calculate_quantity_to_send(quantity, columns)
            labels_data.append((ean, sku, adjusted_quantity))

        if not labels_data:
            messagebox.showerror("Erro", "Nenhum dado válido para gerar etiquetas.")
            return

        self.generator.eans_and_skus.clear()

        for ean, sku, quantity in labels_data:
            if selected_type == "EAN":
                self.generator.add_ean_sku(ean, "", quantity)
            elif selected_type == "SKU":
                self.generator.add_ean_sku("", sku, quantity)
            else:
                self.generator.add_ean_sku(ean, sku, quantity)

        self.generator.set_label_format(label_format)
        self.zpl_code = self.generator.generate_zpl(label_format=label_format)

        if self.zpl_code:
            self.label_text.config(state="normal")
            self.label_text.delete("1.0", tk.END)
            self.label_text.insert("1.0", self.zpl_code)
            self.label_text.config(state="disabled")
            self.print_button.config(state=tk.NORMAL)
            self.select_printer_button.config(state=tk.NORMAL)
            messagebox.showinfo("Sucesso", "Código ZPL gerado com sucesso!")
        else:
            messagebox.showerror("Erro", "Falha ao gerar o código ZPL.")

    def save_zpl(self):
        if not self.zpl_code:
            messagebox.showerror("Erro", "Nenhum código ZPL gerado. Gere antes de salvar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".zpl",
                                                 filetypes=[("Arquivo ZPL", "*.zpl")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(self.zpl_code)
            messagebox.showinfo("Sucesso", f"Arquivo salvo em: {file_path}")