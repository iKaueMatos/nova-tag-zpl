from PIL._tkinter_finder import tk

class CredentialsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciar Credenciais da API")
        self.root.geometry("400x400")

        self.create_widgets()
        self.create_table()

    def create_widgets(self):
        tk.Label(self.root, text="Empresa:").pack()
        self.company_entry = tk.Entry(self.root)
        self.company_entry.pack()

        tk.Label(self.root, text="App Key:").pack()
        self.app_key_entry = tk.Entry(self.root)
        self.app_key_entry.pack()

        tk.Label(self.root, text="App Secret:").pack()
        self.app_secret_entry = tk.Entry(self.root, show="*")
        self.app_secret_entry.pack()

        tk.Label(self.root, text="Client Tax:").pack()
        self.client_tax_entry = tk.Entry(self.root)
        self.client_tax_entry.pack()

        tk.Label(self.root, text="Tax Scenario:").pack()
        self.tax_scenario_entry = tk.Entry(self.root)
        self.tax_scenario_entry.pack()

        tk.Label(self.root, text="Stock Location:").pack()
        self.stock_location_entry = tk.Entry(self.root)
        self.stock_location_entry.pack()

        tk.Button(self.root, text="Salvar", command=self.save_credentials).pack(pady=10)