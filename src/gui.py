import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
import subprocess
import pdf2image
import pytesseract

from .config import OCRConfig
from .ocr_processor import PDFOCRExtractor
from .constants import (
    APP_TITLE,
    APP_VERSION,
    WINDOW_SIZE,
    SUPPORTED_LANGUAGES,
    THEME_CONFIG,
    MAX_RECENT_FILES,
    OUTPUT_SUFFIX,
    SETTINGS_FILE
)

class ExpapyrusGUI:
    """Interfaz gráfica principal de Expapyrus."""
    
    def __init__(self, root: tk.Tk) -> None:
        # Base attributes
        self.root = root
        
        # Settings and state
        self.settings = self.load_settings()
        self.recent_files = []
        self.is_processing = False
        self.processing_thread = None

        # Tkinter variables
        self.file_var = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Listo")
        self.dpi_var = tk.StringVar(value="300")
        self.auto_save_var = tk.BooleanVar(value=True)
        
        # OCR components
        self.ocr_config = None
        self.extractor = None
        
        # GUI components
        self.main_frame = None
        self.process_button = None
        self.progress_bar = None
        self.menubar = None
        
        # Initialize GUI
        try:
            self.setup_window()
            self.setup_styles()
            self.create_widgets()
            self.create_menu()
            self.initialize_ocr()
        except Exception as e:
            logging.error(f"Error de inicialización: {e}")
            messagebox.showerror("Error", f"Error durante la inicialización:\n{str(e)}")
            raise

    def setup_window(self) -> None:
        """Configurar ventana principal."""
        self.root.title(f"{APP_TITLE} - v{APP_VERSION}")
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(600, 400)
        
        # Center window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        self.root.geometry(f"+{x}+{y}")
        
        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def setup_styles(self) -> None:
        """Configurar estilos ttk."""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', padding=6)
        style.configure('TLabel', background='#f0f0f0', padding=5)
        style.configure('TEntry', padding=5)
        style.configure('Horizontal.TProgressbar', thickness=20)

    def create_widgets(self) -> None:
        """Crear y colocar widgets."""
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid
        for i in range(7):
            self.main_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            self.main_frame.grid_columnconfigure(i, weight=1)

        # File selection
        ttk.Label(self.main_frame, text="Seleccionar PDF:").grid(row=0, column=0, sticky="e")
        ttk.Entry(self.main_frame, textvariable=self.file_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(self.main_frame, text="Examinar", command=self.browse_file).grid(row=0, column=2, padx=5)

        # DPI setting
        ttk.Label(self.main_frame, text="DPI:").grid(row=1, column=0, sticky="e")
        ttk.Entry(self.main_frame, textvariable=self.dpi_var, width=10).grid(row=1, column=1, sticky="w", padx=5)

        # Language selection
        ttk.Label(self.main_frame, text="Idioma:").grid(row=2, column=0, sticky="e")
        self.lang_combobox = ttk.Combobox(self.main_frame, values=SUPPORTED_LANGUAGES, state="readonly")
        self.lang_combobox.grid(row=2, column=1, sticky="w", padx=5)
        self.lang_combobox.set(SUPPORTED_LANGUAGES[0])

        # Auto-save option
        ttk.Checkbutton(self.main_frame, text="Auto-guardar", variable=self.auto_save_var).grid(row=3, column=0, columnspan=2, sticky="w")

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.main_frame, mode='determinate', variable=self.progress_var)
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky="ew", pady=10)

        # Status label
        ttk.Label(self.main_frame, textvariable=self.status_var).grid(row=5, column=0, columnspan=3)

        # Process button
        self.process_button = ttk.Button(
            self.main_frame, 
            text="Procesar", 
            command=self.process_file
        )
        self.process_button.grid(row=6, column=1, pady=10)

    def create_menu(self) -> None:
        """Crear menú de la aplicación."""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Abrir", command=self.browse_file)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self.show_about)

    def initialize_ocr(self) -> None:
        """Inicializar configuración OCR y procesador."""
        try:
            self.ocr_config = OCRConfig()
            self.extractor = PDFOCRExtractor(self.ocr_config)
            self.extractor.update_progress = self.update_progress
            logging.info("OCR initialization successful")
        except Exception as e:
            logging.error(f"OCR initialization failed: {e}")
            raise

    def browse_file(self) -> None:
        """Abrir diálogo para seleccionar PDF."""
        filename = filedialog.askopenfilename(
            title="Seleccionar PDF",
            filetypes=[("PDF files", "*.pdf")]
        )
        if filename:
            self.file_var.set(filename)
            self._add_to_recent(filename)

    def process_file(self) -> None:
        """Procesar archivo PDF seleccionado."""
        if not self.file_var.get():
            messagebox.showwarning("Advertencia", "No se ha seleccionado ningún archivo PDF")
            return
        
        self.process_button.config(state='disabled')
        self.progress_var.set(0)
        self.status_var.set("Procesando...")
        self.is_processing = True
        
        self.processing_thread = threading.Thread(
            target=self._process_thread, 
            daemon=True
        )
        self.processing_thread.start()

    def _process_thread(self) -> None:
        """Hilo de procesamiento en segundo plano."""
        try:
            pdf_path = Path(self.file_var.get())
            extracted_text = self.extractor.process_pdf(pdf_path)
            
            if extracted_text and self.auto_save_var.get():
                self._save_output(pdf_path, extracted_text)
            
            self.status_var.set("¡Procesamiento completado!")
        except Exception as e:
            logging.error(f"Error en el procesamiento: {e}")
            self.status_var.set("Error en el procesamiento")
            messagebox.showerror("Error", str(e))
        finally:
            self.is_processing = False
            self.process_button.config(state='normal')

    def _save_output(self, pdf_path: Path, text: str) -> None:
        """Guardar texto extraído a archivo."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = pdf_path.parent / f"{pdf_path.stem}_{timestamp}{OUTPUT_SUFFIX}"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            self.status_var.set(f"Guardado en: {output_path.name}")
        except Exception as e:
            logging.error(f"Error guardando archivo: {e}")
            raise

    def _add_to_recent(self, filepath: str) -> None:
        """Añadir archivo a lista de recientes."""
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        self.recent_files.insert(0, filepath)
        if len(self.recent_files) > MAX_RECENT_FILES:
            self.recent_files = self.recent_files[:MAX_RECENT_FILES]
        self.save_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Cargar configuración desde archivo."""
        if not os.path.exists(SETTINGS_FILE):
            return {}
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            return {}

    def save_settings(self) -> None:
        """Guardar configuración a archivo."""
        try:
            settings = {
                "recent_files": self.recent_files
            }
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving settings: {e}")

    def update_progress(self, value: float) -> None:
        """Actualizar barra de progreso."""
        self.progress_var.set(value)

    def show_about(self) -> None:
        """Mostrar diálogo Acerca de."""
        messagebox.showinfo(
            "Acerca de",
            f"{APP_TITLE}\nVersión {APP_VERSION}\n\nUna aplicación para extraer texto de PDFs."
        )

