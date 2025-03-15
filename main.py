import tkinter as tk

from src.core.database.database import Database
from src.views.barcode.barcode_screen import BarcodeScreen

def main():
    def initialize():
        global root

        root = tk.Tk()
        root.title("Nova Tag")
        root.geometry("1440x900")
        root.iconbitmap("./nova-software-logo.ico")
        root.resizable(True, True)

        root.configure(bg='dark')
        app = BarcodeScreen(root)

        root.bind("<F11>", toggle_fullscreen)
        root.bind("<Escape>", exit_fullscreen)

        Database.create_tables()

        root.mainloop()

    initialize()

def toggle_fullscreen(event=None):
    root.attributes('-fullscreen', not root.attributes('-fullscreen'))

def exit_fullscreen(event=None):
    root.attributes('-fullscreen', False)

if __name__ == "__main__":
    main()
