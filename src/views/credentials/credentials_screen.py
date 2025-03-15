import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
from src.core.database.repositories.credentials_repo import CredentialsRepository

class CredentialsScreen:
    def __init__(self, root):
        self.root = root
        self.window = tk.Toplevel(root)
        self.window.title("Gerenciar Credenciais da API")
        self.window.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.window, padding="10")
        frame.grid(row=0, column=0, sticky="nsew")

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

        ttk.Label(frame, text="Empresa:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.company_entry = ttk.Entry(frame)
        self.company_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="App Key:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.app_key_entry = ttk.Entry(frame)
        self.app_key_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="App Secret:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.app_secret_entry = ttk.Entry(frame, show="*")
        self.app_secret_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Salvar", command=self.save_credentials).pack(side="left", padx=5)

        link_frame = ttk.Frame(frame)
        link_frame.grid(row=8, column=0, columnspan=2, pady=10)
        link_label = ttk.Label(link_frame, text="Clique aqui para obter a chave de acesso para integrações de API", foreground="blue", cursor="hand2")
        link_label.pack()
        link_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://ajuda.omie.com.br/pt-BR/articles/499061-obtendo-a-chave-de-acesso-para-integracoes-de-api"))

    def save_credentials(self):
        company = self.company_entry.get()
        app_key = self.app_key_entry.get()
        app_secret = self.app_secret_entry.get()

        CredentialsRepository.insert_credentials(company, app_key, app_secret)
        messagebox.showinfo("Sucesso", "Credenciais salvas com sucesso!")