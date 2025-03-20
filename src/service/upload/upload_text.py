# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
from tkinter import filedialog, messagebox
from PIL._tkinter_finder import tk

class UploadText:

    @staticmethod
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

    @staticmethod
    def is_valid_zpl(content):
        """Verifica se o conteúdo do arquivo é um código ZPL válido."""
        return "^XA" in content and "^XZ" in content