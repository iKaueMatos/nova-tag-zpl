import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class TemplateDownloadService:
    def __init__(self, root):
        self.root = root

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