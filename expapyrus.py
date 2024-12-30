"""
Expapyrus: From physical images to digital text.
Author: Alejandro Domingo Agustí
Version: 1.0.8
"""

# Importaciones de la biblioteca estándar
import logging
import os
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# Importaciones de terceros
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Importaciones para la GUI
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# Constantes
DEFAULT_DPI = 300
SUPPORTED_LANGUAGES = 'eng+spa+cat'
PLACEHOLDER_TEXT = "[VOID DUE TO UNREADABLE HANDWRITTEN TEXT]"
OUTPUT_SUFFIX = "_extracted_text.txt"

# Configuración del registro (logging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('expapyrus.log', encoding='utf-8')
    ]
)


@dataclass
class OCRConfig:
    """Configuración para el procesamiento OCR."""
    base_path: str = r'C:\Program Files\Tesseract-OCR'
    tesseract_path: str = None
    tessdata_path: str = None
    dpi: int = DEFAULT_DPI
    languages: str = SUPPORTED_LANGUAGES

    def __post_init__(self):
        """Configura las rutas y variables de entorno."""
        self.tesseract_path = os.path.join(self.base_path, 'tesseract.exe')
        self.tessdata_path = os.path.join(self.base_path, 'tessdata')

        if not os.path.exists(self.tesseract_path):
            raise FileNotFoundError(f"No se encontró Tesseract en: {self.tesseract_path}")

        if not os.path.exists(self.tessdata_path):
            raise FileNotFoundError(f"No se encontró Tessdata en: {self.tessdata_path}")

        os.environ['TESSDATA_PREFIX'] = self.base_path
        os.environ['PATH'] = f"{self.base_path};{os.environ['PATH']}"
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path

        # Depuración adicional
        logging.info(f"TESSDATA_PREFIX establecido en: {os.environ['TESSDATA_PREFIX']}")
        logging.info(f"Ruta a tessdata: {self.tessdata_path}")


class PDFOCRExtractor:
    """Clase para el procesamiento OCR de PDFs."""

    def __init__(self, config: OCRConfig):
        self.config = config
        self.temp_dir = Path(tempfile.mkdtemp())
        self._verify_tesseract_setup()

    def process_pdf(self, pdf_path: Path) -> Optional[str]:
        """Procesa un archivo PDF y extrae el texto."""
        try:
            logging.info(f"Procesando PDF: {pdf_path}")

            if not pdf_path.exists():
                raise FileNotFoundError(f"Archivo PDF no encontrado: {pdf_path}")

            # Convertir PDF a imágenes
            images = convert_from_path(
                str(pdf_path),
                dpi=self.config.dpi,
                output_folder=str(self.temp_dir),
                poppler_path=r'C:\Program Files\poppler-24.08.0\Library\bin'
            )

            if not images:
                raise ValueError("No se extrajeron imágenes del PDF")

            return self._process_images(images)

        except Exception as e:
            logging.error(f"Fallo en el procesamiento del PDF: {e}")
            raise
        finally:
            self._cleanup()

    def _process_images(self, images: List[Image.Image]) -> str:
        """Procesa las imágenes y extrae el texto."""
        all_text = []

        total_pages = len(images)
        for idx, image in enumerate(images, 1):
            try:
                temp_image_path = self.temp_dir / f"temp_page_{idx}.png"
                image.save(temp_image_path, 'PNG')

                text = pytesseract.image_to_string(
                    Image.open(temp_image_path),
                    lang=self.config.languages
                    # Eliminar el argumento --tessdata-dir
                    # Si aún necesitas especificarlo, asegúrate de que la ruta es correcta
                )

                all_text.append(f"Página {idx}\n\n{text.strip()}")

                # Actualizar la barra de progreso
                progress = (idx / total_pages) * 100
                logging.info(f"Procesada página {idx}/{total_pages} ({progress:.2f}%)")
                # Pasar "progress" a la GUI
                if hasattr(self, 'update_progress'):
                    self.update_progress(progress)

            except Exception as e:
                logging.error(f"Error procesando la página {idx}: {e}")
                all_text.append(f"Página {idx}\n\n[ERROR DE PROCESAMIENTO]")
            finally:
                if temp_image_path.exists():
                    temp_image_path.unlink()

        return '\n\n'.join(all_text)

    def _verify_tesseract_setup(self):
        """Verifica la instalación de Tesseract."""
        try:
            version = pytesseract.get_tesseract_version()
            logging.info(f"Versión de Tesseract: {version}")

            for lang in self.config.languages.split('+'):
                lang_file = Path(self.config.tessdata_path) / f"{lang}.traineddata"
                if not lang_file.exists():
                    raise FileNotFoundError(f"Archivo de idioma no encontrado: {lang_file}")

        except Exception as e:
            logging.error(f"Fallo en la verificación de Tesseract: {e}")
            raise

    def _cleanup(self):
        """Limpia los archivos temporales."""
        try:
            for file in self.temp_dir.glob('*'):
                try:
                    file.unlink()
                except Exception as e:
                    logging.warning(f"No se pudo eliminar el archivo temporal {file}: {e}")
            self.temp_dir.rmdir()
        except Exception as e:
            logging.error(f"Fallo en la limpieza: {e}")


class ExpapyrusGUI:
    """Clase para la interfaz gráfica de Expapyrus."""

    def __init__(self, root):
        self.root = root
        self.root.title("Expapyrus")
        self.root.geometry("600x250")
        self.root.resizable(False, False)

        # Variables
        self.file_var = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar()

        # Inicializar configuración OCR
        try:
            self.ocr_config = OCRConfig()
        except FileNotFoundError as e:
            messagebox.showerror("Configuración de OCR", str(e))
            self.root.destroy()
            return

        # Extractor
        self.extractor = PDFOCRExtractor(self.ocr_config)
        # Vincular el método de actualización de progreso
        self.extractor.update_progress = self.update_progress

        # Widgets
        self.create_widgets()

    def create_widgets(self):
        """Crea y coloca los widgets en la interfaz."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Selección de archivo
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=0, column=0, sticky="w", pady=5)

        file_label = ttk.Label(file_frame, text="Selecciona un archivo PDF:")
        file_label.pack(side=tk.LEFT, padx=(0, 5))

        file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=50, state='readonly')
        file_entry.pack(side=tk.LEFT, padx=(0, 5))

        browse_button = ttk.Button(file_frame, text="Buscar", command=self._browse_file)
        browse_button.pack(side=tk.LEFT)

        # Botón de procesar
        process_button = ttk.Button(main_frame, text="Procesar", command=self._process_file)
        process_button.grid(row=1, column=0, pady=10, sticky="w")

        # Estado
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=2, column=0, sticky="w")

        # Barra de progreso
        progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        progress_bar.grid(row=3, column=0, sticky="we", pady=(5, 0))

    def _browse_file(self):
        """Abre un cuadro de diálogo para seleccionar un archivo PDF."""
        file_path = filedialog.askopenfilename(
            title="Selecciona un archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if file_path:
            self.file_var.set(file_path)
            self.status_var.set("Archivo seleccionado.")
            logging.info(f"Archivo seleccionado: {file_path}")

    def _process_file(self):
        """Inicia el procesamiento del archivo seleccionado."""
        if not self.file_var.get():
            messagebox.showwarning("Advertencia", "Por favor, selecciona un archivo PDF para procesar.")
            return

        # Deshabilitar botones durante el procesamiento
        self._toggle_widgets(state='disabled')
        self.status_var.set("Procesando...")
        self.progress_var.set(0)
        logging.info("Inicio del procesamiento del archivo.")

        # Iniciar el procesamiento en un hilo separado
        threading.Thread(target=self._run_ocr, daemon=True).start()

    def _run_ocr(self):
        """Ejecuta el OCR y actualiza la interfaz."""
        pdf_path = Path(self.file_var.get())
        try:
            # Procesamiento OCR
            extracted_text = self.extractor.process_pdf(pdf_path)

            # Guardar el texto extraído
            output_path = pdf_path.parent / f"{pdf_path.stem}{OUTPUT_SUFFIX}"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(extracted_text)

            logging.info(f"Texto extraído guardado en: {output_path}")

            # Actualizar la interfaz
            self.root.after(0, lambda: self.status_var.set(f"Proceso completado.\nTexto guardado en: {output_path}"))
            messagebox.showinfo("Éxito", f"Texto extraído y guardado en:\n{output_path}")

        except Exception as e:
            logging.error(f"Error durante el procesamiento OCR: {e}")
            self.root.after(0, lambda: self.status_var.set("Error durante el procesamiento. Revisa el log para más detalles."))
            messagebox.showerror("Error", f"Hubo un error durante el procesamiento:\n{e}")

        finally:
            # Rehabilitar los widgets
            self.root.after(0, lambda: self._toggle_widgets(state='!disabled'))

    def _toggle_widgets(self, state: str):
        """Habilita o deshabilita los widgets durante el procesamiento."""
        for child in self.root.winfo_children():
            for subchild in child.winfo_children():
                if isinstance(subchild, ttk.Button) or isinstance(subchild, ttk.Entry):
                    if state == 'disabled':
                        subchild.state(['disabled'])
                    elif state == '!disabled':
                        subchild.state(['!disabled'])
                if isinstance(subchild, ttk.Progressbar):
                    if state == 'disabled':
                        subchild.state(['disabled'])
                    elif state == '!disabled':
                        subchild.state(['!disabled'])

    def update_progress(self, value):
        """Actualiza la barra de progreso."""
        self.progress_var.set(value)
        self.root.update_idletasks()


def main():
    """Función principal para ejecutar la GUI."""
    root = tk.Tk()
    app = ExpapyrusGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()