# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, filedialog
from PIL import Image, ImageTk
import io

from src.infra.repositories.printer_repo import PrinterRepository
from src.utils.dialog_center import DialogCenter


class ZPLManualView:
    def __init__(self, parent, printer_service, zebra_labelary_api_service):
        self.printer_service = printer_service
        self.zebra_labelary_api_service = zebra_labelary_api_service
        self.parent = parent

        self.window = tk.Toplevel(parent)
        self.window.title("Nova Tag - Inserção Manual de Código ZPL")
        self.window.geometry("1440x1000")

        if sys.platform.startswith("win"):
            try:
                self.window.iconbitmap("./nova-software-logo.ico")
            except Exception as e:
                print(f"Erro ao carregar ícone no Windows: {e}")
        elif sys.platform.startswith("linux"):
            try:
                self.window.iconbitmap("@./nova-software-logo.png")
            except Exception as e:
                print(f"Erro ao carregar ícone no Linux: {e}")

        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.build_menu_bar()
        self.build_layout()
        self.minimize_main_window()
        self.check_existing_printer()

    def on_close(self):
        """Reexibe a janela principal ao fechar a secundária"""
        self.parent.deiconify()
        self.window.destroy()

    def build_menu_bar(self):
        self.menu_bar = tk.Menu(self.window)
        self.window.config(menu=self.menu_bar)

        self.config_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Configurações", menu=self.config_menu)

        self.config_menu.add_command(label="Selecionar Impressora", command=self.select_printer, accelerator="Ctrl+P")
        self.advanced_config_menu = tk.Menu(self.config_menu, tearoff=0)
        self.config_menu.add_cascade(label="Configurações Avançadas", menu=self.advanced_config_menu)
        self.advanced_config_menu.add_command(label="Ajustar Densidade", command=self.adjust_density)
        self.config_menu.add_command(label="Limpar Fila de Impressão", command=self.clear_print_queue)

    def build_layout(self):
        left_frame = ttk.Frame(self.window, padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(left_frame, text="Código ZPL Inserido:", font=("Helvetica", 12, "bold")).pack(anchor="w")
        self.zpl_textarea = scrolledtext.ScrolledText(left_frame, width=50, height=30, font=("Courier", 10))
        self.zpl_textarea.pack(expand=True, fill="both")

        right_frame = ttk.Frame(self.window, padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew")

        ttk.Label(right_frame, text="Pré-visualização da Etiqueta:", font=("Helvetica", 12, "bold")).pack(anchor="w",
                                                                                                          pady=(10, 0))
        self.preview_image_label = ttk.Label(right_frame, text="Preview não disponível", relief="sunken",
                                             anchor="center")
        self.preview_image_label.pack(expand=True, fill="both", padx=5, pady=5)

        bottom_config_frame = ttk.Frame(self.window, padding=10)
        bottom_config_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Subframe: Densidade de impressão
        density_frame = ttk.Frame(bottom_config_frame)
        density_frame.pack(side="left", padx=10)

        ttk.Label(density_frame, text="Densidade de impressão:", font=("Helvetica", 10)).grid(row=0, column=0,
                                                                                              sticky="e", padx=3,
                                                                                              pady=3)
        self.density_combobox = ttk.Combobox(density_frame, values=[
            "6 dpmm (152 dpi)", "8 dpmm (203 dpi)", "12 dpmm (300 dpi)", "24 dpmm (600 dpi)"
        ], state="readonly", width=20)
        self.density_combobox.grid(row=0, column=1, sticky="w", padx=3, pady=3)
        self.density_combobox.current(1)

        size_frame = ttk.Frame(bottom_config_frame)
        size_frame.pack(side="left", padx=10)

        ttk.Label(size_frame, text="Etiqueta (L x A):", font=("Helvetica", 10)).grid(row=0, column=0, sticky="e",
                                                                                     padx=3, pady=3)
        self.label_width_entry = ttk.Entry(size_frame, width=5)
        self.label_width_entry.insert(0, "4")
        self.label_width_entry.grid(row=0, column=1, padx=(0, 3), pady=3)

        ttk.Label(size_frame, text="x").grid(row=0, column=2, padx=2)

        self.label_height_entry = ttk.Entry(size_frame, width=5)
        self.label_height_entry.insert(0, "6")
        self.label_height_entry.grid(row=0, column=3, padx=(0, 3), pady=3)

        self.label_unit_combobox = ttk.Combobox(size_frame, values=["inches", "cm", "mm"], width=7, state="readonly")
        self.label_unit_combobox.current(0)
        self.label_unit_combobox.grid(row=0, column=4, padx=3, pady=3)

        labels_frame = ttk.Frame(bottom_config_frame)
        labels_frame.pack(side="left", padx=10)

        ttk.Label(labels_frame, text="Rótulo atual:", font=("Helvetica", 10)).grid(row=0, column=0, sticky="e", padx=3,
                                                                                   pady=3)
        self.show_label_entry = ttk.Entry(labels_frame, width=5)
        self.show_label_entry.insert(0, "1")
        self.show_label_entry.grid(row=0, column=1, padx=3, pady=3)

        ttk.Label(labels_frame, text="Total de rótulos:", font=("Helvetica", 10)).grid(row=0, column=2, sticky="e",
                                                                                       padx=3, pady=3)
        self.total_labels_entry = ttk.Entry(labels_frame, width=5, state="disabled")
        self.total_labels_entry.insert(0, "1")
        self.total_labels_entry.grid(row=0, column=3, padx=3, pady=3)

        button_frame = ttk.Frame(self.window, padding=10)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.preview_button = ttk.Button(button_frame, text="Gerar Preview", command=self.generate_preview)
        self.preview_button.pack(side="left", padx=5, pady=5)

        self.print_button = ttk.Button(button_frame, text="Imprimir", command=self.print_zpl)
        self.print_button.pack(side="left", padx=5, pady=5)

        self.upload_button = ttk.Button(button_frame, text="Upload Arquivo", command=self.upload_file)
        self.upload_button.pack(side="left", padx=5, pady=5)

    def generate_preview(self):
        zpl_code = self.zpl_textarea.get("1.0", tk.END).strip()
        if not zpl_code:
            messagebox.showwarning("Atenção", "Insira um código ZPL para gerar o preview.")
            return

        try:
            unit = self.label_unit_combobox.get()
            width = float(self.label_width_entry.get())
            height = float(self.label_height_entry.get())
            width_in_inches = self.convert_to_inches(width, unit)
            height_in_inches = self.convert_to_inches(height, unit)

            density_mapping = {
                "6 dpmm (152 dpi)": "6dpmm",
                "8 dpmm (203 dpi)": "8dpmm",
                "12 dpmm (300 dpi)": "12dpmm",
                "24 dpmm (600 dpi)": "24dpmm"
            }
            selected_density_text = self.density_combobox.get()
            density = density_mapping.get(selected_density_text, "8dpmm")  # fallback padrão

            image_data = self.zebra_labelary_api_service.generate_preview_image(
                zpl_code,
                density,
                f"{width_in_inches}x{height_in_inches}",
            )

            if image_data:
                image = image_data.resize((350, 350), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.preview_image_label.configure(image=photo, text="")
                self.preview_image_label.image = photo
            else:
                messagebox.showerror("Erro", "Não foi possível gerar a imagem desta etiqueta.")

        except ValueError:
            messagebox.showerror("Erro", "As dimensões da etiqueta devem ser numéricas.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar preview: {e}")

    def minimize_main_window(self):
        self.parent.iconify()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def print_zpl(self):
        zpl_code = self.zpl_textarea.get("1.0", tk.END).strip()
        if not zpl_code:
            messagebox.showwarning("Atenção", "Insira um código ZPL para imprimir.")
            return
        try:
            self.printer_service.print_label(zpl_code)
            messagebox.showinfo("Sucesso", "Impressão enviada para a impressora.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao imprimir: {e}")

    def clear_print_queue(self):
        """Limpa a fila de impressão utilizando o serviço de impressora Zebra."""
        self.printer_service.clear_print_queue()

    def adjust_density(self):
        """Permite ao usuário ajustar a densidade de impressão através de uma caixa de entrada."""
        density_value = simpledialog.askinteger("Ajustar Densidade", "Escolha a densidade de 0 a 30:",
                                                minvalue=0, maxvalue=30, initialvalue=self.printer_service.density)
        DialogCenter.center_window(density_value)
        if density_value is not None:
            self.printer_service.set_density(density_value)
            messagebox.OK

    def select_printer(self):
        printers = self.printer_service.get_printers()
        if not printers:
            messagebox.showerror("Erro", "Nenhuma impressora disponível.")
            return

        def confirm_selection():
            selected = printer_var.get()
            if selected in printers:
                self.printer_service.set_printer(selected)
                messagebox.showinfo("Sucesso", f"Impressora selecionada: {selected}")
                popup.destroy()
            else:
                messagebox.showwarning("Aviso", "Selecione uma impressora válida.")

        popup = tk.Toplevel(self.window)
        popup.title("Selecionar Impressora")
        popup.geometry("400x200")
        popup.grab_set()
        DialogCenter.center_window(popup)

        tk.Label(popup, text="Escolha uma impressora:").pack(pady=5)

        printer_var = tk.StringVar(value=printers[0])

        printer_combobox = ttk.Combobox(popup, textvariable=printer_var, values=printers, state="readonly")
        printer_combobox.pack(pady=10, padx=10, fill="x")
        printer_combobox.config(width=30)
        printer_combobox.current(0)
        ttk.Button(popup, text="Confirmar", command=confirm_selection).pack(pady=10)

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Arquivos de Texto", "*.txt"), ("Arquivos ZPL", "*.zpl")])
        if not file_path:
            return

        try:
            with open(file_path, "r") as file:
                content = file.read().strip()
                if not content:
                    messagebox.showwarning("Aviso", "O arquivo está vazio.")
                    return

                if not self.is_valid_zpl(content):
                    messagebox.showerror("Erro", "O conteúdo do arquivo não é um código ZPL válido.")
                    return

                self.zpl_textarea.delete("1.0", tk.END)
                self.zpl_textarea.insert("1.0", content)
                messagebox.showinfo("Sucesso", f"Arquivo '{file_path}' carregado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar o arquivo: {e}")

    def is_valid_zpl(self, content):
        """Verifica se o conteúdo do arquivo é um código ZPL válido."""
        return "^XA" in content and "^XZ" in content

    def check_existing_printer(self):
        printers = PrinterRepository.list_all_printers()
        if printers:
            self.selected_printer = printers[0]['option_printer']
            self.print_button.config(state=tk.NORMAL)
        else:
            self.print_button.config(state=tk.DISABLED)

    def convert_to_inches(self, value, unit):
        try:
            value = float(value)
            if unit == "mm":
                return value / 25.4
            elif unit == "cm":
                return value / 2.54
            return value
        except ValueError:
            return 0