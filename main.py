import tkinter as tk
from tkinter import ttk
from src.views.barcode_label_app import BarcodeLabelApp

def main():
    global root
    root = tk.Tk()
    root.title("Tag - Gerador de etiquetas Zpl")

    root.geometry("1440x900")
    root.configure(bg='#f0f0f0')
    root.iconbitmap("./tag.ico")

    root.resizable(True, True)
    app = BarcodeLabelApp(root)

    root.bind("<F11>", toggle_fullscreen)
    root.bind("<Escape>", exit_fullscreen)

    root.mainloop()

def toggle_fullscreen(event=None):
    """Alterna entre tela cheia e modo janela."""
    state = root.attributes('-fullscreen')
    root.attributes('-fullscreen', not state)

def exit_fullscreen(event=None):
    """Sai do modo tela cheia (pressionando ESC)."""
    root.attributes('-fullscreen', False)


if __name__ == "__main__":
    main()
