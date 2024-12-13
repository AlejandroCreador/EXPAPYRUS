import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
import logging
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox

def configure_logger():
    # Configuración básica del logger
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler()])

class PDFOCRExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.temp_dir = tempfile.mkdtemp()
        configure_logger()
        
        # Configuración de pytesseract (asegúrate de que esté en el PATH o configura la ruta manualmente)
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR'  # Cambia según tu instalación

    def convert_pdf_to_images(self):
        logging.info("Convirtiendo el PDF a imágenes...")
        try:
            images = convert_from_path(self.pdf_path, dpi=300, output_folder=self.temp_dir)
            logging.info(f"Total de páginas convertidas: {len(images)}")
            return images
        except Exception as e:
            logging.error(f"Error durante la conversión del PDF: {e}")
            return []

    def extract_text_from_image(self, image):
        logging.info("Extrayendo texto de la imagen...")
        try:
            # Utiliza Tesseract para extraer el texto de la imagen.
            text = pytesseract.image_to_string(image, lang='eng+spa+cat')
            logging.info("Extracción de texto completada con éxito.")
            return text
        except Exception as e:
            logging.error(f"Error al extraer el texto: {e}")
            return ""

    def extract_text_from_pdf(self):
        logging.info("Iniciando extracción de texto del PDF...")
        images = self.convert_pdf_to_images()
        if not images:
            logging.error("No se pudieron convertir las páginas del PDF. Proceso abortado.")
            return ""
        
        all_text = []
        for index, image in enumerate(images):
            text = self.extract_text_from_image(image)
            formatted_text = self.format_extracted_text(text)
            all_text.append(f"Página {index + 1}\n\n" + formatted_text)
        logging.info("Extracción de texto del PDF finalizada.")
        return '\n\n'.join(all_text)

    def format_extracted_text(self, text):
        logging.info("Formateando el texto extraído...")
        placeholder = "[VACÍO POR TEXTO MANUSCRITO NO LEGIBLE]"
        formatted_text = re.sub(r'\n{3,}', '\n\n', text)  # Limita saltos de línea consecutivos a un máximo de 2.
        formatted_text = re.sub(r'\s+', ' ', formatted_text).strip()  # Elimina espacios en blanco excesivos.
        formatted_text = re.sub(r'\.{2,}', placeholder, formatted_text)  # Detecta "..." y similares.
        formatted_text = re.sub(r'_{2,}', placeholder, formatted_text)  # Detecta guiones bajos repetidos.
        return formatted_text

    def save_text_to_file(self, output_path, text):
        logging.info(f"Guardando el texto extraído en {output_path}...")
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            logging.info("Texto guardado con éxito.")
        except Exception as e:
            logging.error(f"Error al guardar el archivo de texto: {e}")

    def clean_up(self):
        logging.info("Limpiando archivos temporales...")
        try:
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)
            logging.info("Archivos temporales eliminados.")
        except Exception as e:
            logging.error(f"Error durante la limpieza de archivos temporales: {e}")

def main():
    # Crear una ventana oculta de Tkinter
    root = tk.Tk()
    root.withdraw()

    # Mostrar un cuadro de diálogo para seleccionar el archivo PDF
    pdf_path = filedialog.askopenfilename(
        title="Seleccionar archivo PDF",
        filetypes=[("Archivos PDF", "*.pdf")])

    if not pdf_path:
        messagebox.showinfo("Información", "No se seleccionó ningún archivo. El programa se cerrará.")
        return

    # Definir la ruta de salida
    output_dir = os.path.dirname(pdf_path)
    output_filename = os.path.splitext(os.path.basename(pdf_path))[0] + "_texto_extraido.txt"
    output_path = os.path.join(output_dir, output_filename)

    # Crear instancia del extractor OCR
    extractor = PDFOCRExtractor(pdf_path)

    # Extraer texto y guardar en un archivo de salida
    extracted_text = extractor.extract_text_from_pdf()
    if extracted_text.strip():  # Verifica que haya texto extraído antes de guardar
        extractor.save_text_to_file(output_path, extracted_text)
        messagebox.showinfo("Proceso completado", f"El texto extraído se ha guardado en:\n{output_path}")
    else:
        logging.warning("No se extrajo texto del PDF.")
        messagebox.showwarning("Proceso incompleto", "No se pudo extraer texto del PDF.")

    # Limpieza de los archivos temporales
    extractor.clean_up()

if __name__ == "__main__":
    main()
