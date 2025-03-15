import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["tkinter", "pandas", "openpyxl", "reportlab", "os", "shutil", "requests", "zebra", "http", "plyer"],
    "includes": ["src.views.barcode_label_app"],
    "excludes": ["unittest", "email", "http", "pdb"],
    "include_files": [
        ("./nova-software-logo.ico", "nova-software-logo.ico"),
    ]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

exe = Executable(
    script="main.py",
    base=base,
    icon="./nova-software-logo.ico",
    target_name="Nova-software-tag.exe",
    shortcut_name="Nova Software Tag",
    copyright="©2025 Nova Software",
)

setup(
    name="Nova Software Tag",
    version="1.1",
    description="Aplicativo para gerar etiquetas ZPL",
    options={"build_exe": build_exe_options},
    executables=[exe],
)