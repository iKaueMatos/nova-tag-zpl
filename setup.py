import sys
from cx_Freeze import setup, Executable
import os

build_exe_options = {
    "packages": ["tkinter", "pandas", "openpyxl", "reportlab", "os", "shutil", "requests", "zebra", "http"],
    "includes": ["src.views.barcode_label_app"],
    "excludes": ["unittest", "email", "http", "pdb"],
    "include_files": [
        ("./tag.ico", "tag.ico"),
    ]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

exe = Executable(
    script="main.py",
    base=base,
    icon="./tag.ico",
    target_name="TagApp.exe",
    shortcut_name="Tag Gerador",
    copyright="© 2025 Kauê de Matos ou Nova Software",
)

setup(
    name="Tag",
    version="1.0",
    description="Aplicativo para gerar etiquetas ZPL",
    options={"build_exe": build_exe_options},
    executables=[exe],
)
