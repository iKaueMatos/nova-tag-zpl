import tkinter as tk
from tkinter import ttk
from src.views.barcode_label_app import BarcodeLabelApp

def main():
    root = tk.Tk()
    root.title("Gerador de Etiquetas - ZPL")
    
    root.geometry("1024x720")
    root.configure(bg='#f0f0f0')
    
    root.resizable(False, False)
    app = BarcodeLabelApp(root)

    root.mainloop()

if __name__ == "__main__":
    main()
