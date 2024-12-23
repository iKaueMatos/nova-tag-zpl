import tkinter as tk
from src.views.barcode_label_app import BarcodeLabelApp

def main():
    root = tk.Tk()
    root.title("ZPL Labels")
    root.geometry("620x380")
    root.configure(bg='lightgray')
    app = BarcodeLabelApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()