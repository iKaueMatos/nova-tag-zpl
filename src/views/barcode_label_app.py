import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext
import math
from PIL import Image, ImageTk

from src.enum.LabelFormatConstants import LabelFormatConstants
from src.models.barcode_label_generator import BarcodeLabelGenerator
from src.service.download_template_service import TemplateDownloadService
from src.service.sheet_importer import SheetImporter
from src.service.zebra_labelary_api_service import ZebraLabelaryApiService
from src.service.zebra_printer_service import ZebraPrinterService

class BarcodeLabelApp:
    def __init__(self, root):
        self.generator = BarcodeLabelGenerator()
        self.printer_service = ZebraPrinterService()
        self.zpl_code = None
        self.selected_printer = None
        self.zebra_labelary_api_service = ZebraLabelaryApiService()
        self.root = root

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        left_frame = ttk.Frame(root, padding=20)
        left_frame.grid(row=0, column=0, sticky="nsew")

        self.right_frame = ttk.Frame(root, padding=20)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        ttk.Label(left_frame, text="Tipo de Código:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.code_type = tk.StringVar(value="EAN")
        self.code_type_combobox = ttk.Combobox(left_frame, textvariable=self.code_type, state="readonly")
        self.code_type_combobox['values'] = ("EAN", "SKU", "Ambos")
        self.code_type_combobox.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.code_type_combobox.bind("<<ComboboxSelected>>", self.toggle_fields)

        ttk.Label(left_frame, text="Formato da Etiqueta:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.label_format = tk.StringVar(value="1-Coluna")
        self.format_combobox = ttk.Combobox(left_frame, textvariable=self.label_format, state="readonly")
        self.format_combobox['values'] = ("1-Coluna", "2-Colunas")
        self.format_combobox.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(left_frame, text="EAN:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.ean_entry = ttk.Entry(left_frame)
        self.ean_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(left_frame, text="SKU:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.sku_entry = ttk.Entry(left_frame)
        self.sku_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(left_frame, text="Quantidade:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.quantity_entry = ttk.Entry(left_frame, width=10)
        self.quantity_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        self.add_button = ttk.Button(left_frame, text="Adicionar", command=self.add_entry)
        self.add_button.grid(row=4, column=2, sticky="e", padx=5, pady=5)

        tree_frame = ttk.Frame(left_frame)
        tree_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
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
        left_frame.rowconfigure(5, weight=1)

        ttk.Label(left_frame, text="Código ZPL Gerado:").grid(row=6, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        self.label_text = scrolledtext.ScrolledText(left_frame, width=50, height=10, state=tk.DISABLED)
        self.label_text.grid(row=7, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        left_frame.rowconfigure(7, weight=1)

        button_frame1 = ttk.Frame(left_frame)
        button_frame1.grid(row=8, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.importer = SheetImporter(self.generator, self.tree, self.code_type)
        self.import_button = ttk.Button(button_frame1, text="Importar Planilha", command=self.import_sheet)
        self.import_button.pack(side="left", expand=True, fill="both")
        self.generate_button = ttk.Button(button_frame1, text="Gerar ZPL", command=self.generate_zpl)
        self.generate_button.pack(side="left", expand=True, fill="both")
        self.clear_button = ttk.Button(button_frame1, text="Limpar Dados", command=self.clear_data)
        self.clear_button.pack(side="left", expand=True, fill="both")

        button_frame2 = ttk.Frame(left_frame)
        button_frame2.grid(row=9, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        self.select_printer_button = ttk.Button(button_frame2, text="Selecionar Impressora",
                                                command=self.select_printer, state=tk.DISABLED)
        self.select_printer_button.pack(side="left", expand=True, fill="both")
        self.print_button = ttk.Button(button_frame2, text="Imprimir", command=self.print_label, state=tk.DISABLED)
        self.print_button.pack(side="left", expand=True, fill="both")

        self.template_download_service = TemplateDownloadService(self.root)
        self.download_button = ttk.Button(button_frame2, text="Baixar Template", command=self.download_template)
        self.download_button.pack(side="left", expand=True, fill="both")

        self.save_button = ttk.Button(button_frame2, text="Salvar ZPL", command=self.save_zpl)
        self.save_button.pack(side="left", expand=True, fill="both")

        self.preview_label = ttk.Label(self.right_frame, text="Imagem da Etiqueta")
        self.preview_label.grid(row=0, column=0, pady=10)

        preview_frame = ttk.LabelFrame(self.right_frame, text="Pré-visualização da Etiqueta")
        preview_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.preview_image_label = ttk.Label(preview_frame)
        self.preview_image_label.pack(expand=True, fill="both", padx=5, pady=5)
        self.update_preview_button = ttk.Button(self.right_frame, text="Atualizar Preview", command=self.update_preview)
        self.update_preview_button.grid(row=2, column=0, pady=10)

        self.root.bind("<Control-a>", self.select_all_rows)
        self.tree.bind("<ButtonRelease-1>", self.on_row_click)
        self.root.bind('<Return>', lambda event: self.generate_zpl())
        self.toggle_fields()

    def update_preview(self):
        """
            Gera a imagem a partir do ZPL (via Labelary) e exibe no Label de preview.
        """
        if not self.zpl_code:
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

        if selected_label_format == "2-Colunas":
            printer_density = LabelFormatConstants.PRINTER_DENSITY_8DPMM
            label_dimensions = LabelFormatConstants.LABEL_DIMENSIONS_5X25
            label_index = LabelFormatConstants.LABEL_INDEX_0
            output_format = LabelFormatConstants.OUTPUT_FORMAT_IMAGE

        if selected_label_format == "1-Coluna":
            printer_density = LabelFormatConstants.PRINTER_DENSITY_8DPMM
            label_dimensions = LabelFormatConstants.LABEL_DIMENSIONS_5X25
            label_index = LabelFormatConstants.LABEL_INDEX_0
            output_format = LabelFormatConstants.OUTPUT_FORMAT_IMAGE

        image = self.zebra_labelary_api_service.generate_preview_image(
            zpl_code_to_send,
            printer_density,
            label_dimensions,
            label_index,
            output_format
        )

        if image:
            width, height = image.size
            new_width = 600
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

        def confirm_selection():
            selected = printer_var.get()
            if selected in printers:
                self.selected_printer = selected
                self.printer_service.set_printer(selected)
                messagebox.showinfo("Sucesso", f"Impressora selecionada: {selected}")
                popup.destroy()
            else:
                messagebox.showwarning("Aviso", "Selecione uma impressora válida.")

        popup = tk.Toplevel(self.root)
        popup.title("Selecionar Impressora")
        popup.geometry("350x200")
        popup.grab_set()

        tk.Label(popup, text="Escolha uma impressora:").pack(pady=5)

        printer_var = tk.StringVar(value=printers[0])

        printer_combobox = ttk.Combobox(popup, textvariable=printer_var, values=printers, state="readonly")
        printer_combobox.pack(pady=10, padx=10, fill="x")
        printer_combobox.config(width=30)
        printer_combobox.current(0)

        ttk.Button(popup, text="Confirmar", command=confirm_selection).pack(pady=10)

    def print_label(self):
        if not self.selected_printer:
            messagebox.showerror("Erro", "Selecione uma impressora antes de imprimir.")
            return

        zpl_data = self.label_text.get("1.0", tk.END).strip()
        if not zpl_data:
            messagebox.showerror("Erro", "Nenhum código ZPL para imprimir.")
            return

        confirm = messagebox.askyesno("Confirmação", "Deseja realmente imprimir a etiqueta?")
        if not confirm:
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

        self.label_text.config(state=tk.NORMAL)
        self.label_text.delete("1.0", tk.END)
        self.label_text.config(state=tk.DISABLED)

        self.zpl_code = None
        self.print_button.config(state=tk.DISABLED)
        self.select_printer_button.config(state=tk.DISABLED)
        messagebox.showinfo("Sucesso", "Todos os dados foram limpos.")

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

    def import_sheet(self):
        self.importer.import_sheet()

    def download_template(self):
        self.template_download_service.download_template()

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
        self.zpl_code = self.generator.generate_zpl()

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

    def on_row_click(self, event):
        """
            Captura as informações da linha selecionada.
        """
        selected_item = self.tree.selection()
        if selected_item:
            self.update_preview()

    def select_all_rows(self, event=None):
        for item in self.tree.get_children():
            self.tree.selection_add(item)