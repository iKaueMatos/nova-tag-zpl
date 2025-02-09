import tkinter as tk
from tkinter import ttk
from src.views.barcode_label_app import BarcodeLabelApp

def main():
    root = tk.Tk()
    root.title("Gerador de Etiquetas - ZPL")
    
    root.geometry("620x450")
    root.configure(bg='#f0f0f0')
    
    root.resizable(False, False)

    root.option_add("*Font", "Helvetica 10")

    style = ttk.Style()
    style.configure("TButton",
                    padding=6,
                    relief="flat",
                    background="#4CAF50",
                    foreground="white",
                    font=("Helvetica", 10, "bold"))
    style.map("TButton",
              background=[('active', '#45a049')])

    style.configure("TCombobox",
                    padding=6,
                    relief="flat",
                    background="#ffffff",
                    font=("Helvetica", 10))

    style.configure("TEntry",
                    padding=6,
                    relief="flat",
                    font=("Helvetica", 10))

    app = BarcodeLabelApp(root)

    root.mainloop()

if __name__ == "__main__":
    main()
