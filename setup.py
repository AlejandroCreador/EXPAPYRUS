"""Setup configuration for building the application."""

import sys
from cx_Freeze import setup, Executable

# Dependencies
build_exe_options = {
    "packages": [
        "tkinter",
        "PIL",
        "pytesseract",
        "pdf2image",
        "logging",
        "threading",
        "pathlib",
        "webbrowser"
    ],
    "excludes": [],
    "include_files": [
        "assets/",  # Carpeta para iconos, imágenes, etc.
        "LICENSE",
        "README.md",
        ("C:/Program Files/Tesseract-OCR", "tesseract"),  # Incluir Tesseract
        ("C:/Program Files/poppler-24.08.0/Library/bin", "poppler")  # Incluir Poppler
    ]
}

# Executable configuration
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Expapyrus",
    version="1.1.0",
    description="PDF OCR Text Extraction Tool",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="Expapyrus.exe",
            icon="assets/icon.ico",  # Asegúrate de tener un icono
            copyright="Your Company © 2024"
        )
    ]
)