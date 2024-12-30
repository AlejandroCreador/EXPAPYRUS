import subprocess
import logging
from pathlib import Path
from typing import List
from pdf2image import convert_from_path
import tempfile
import os

class PDFOCRExtractor:
    def __init__(self, config):
        self.config = config
        self.update_progress = None

    def process_pdf(self, pdf_path: Path) -> str:
        try:
            # Convertir PDF a imágenes
            with tempfile.TemporaryDirectory() as temp_dir:
                logging.info(f"Converting PDF to images: {pdf_path}")
                images = convert_from_path(
                    pdf_path, 
                    dpi=self.config.dpi,
                    output_folder=temp_dir
                )
                
                extracted_text = []
                total_pages = len(images)
                
                for i, image in enumerate(images):
                    # Guardar imagen temporalmente
                    image_path = os.path.join(temp_dir, f'page_{i}.png')
                    image.save(image_path)
                    
                    # Procesar imagen con Tesseract
                    command = [
                        self.config.tesseract_cmd,
                        image_path,
                        'stdout',
                        '--tessdata-dir',
                        self.config.tessdata_dir,
                        '-l',
                        '+'.join(self.config.languages)
                    ]
                    
                    logging.debug(f"Running Tesseract command: {' '.join(command)}")
                    
                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        check=False  # No lanzar excepción en error
                    )
                    
                    if result.returncode != 0:
                        logging.error(f"Tesseract error: {result.stderr}")
                    else:
                        extracted_text.append(result.stdout)
                    
                    if self.update_progress:
                        progress = ((i + 1) / total_pages) * 100
                        self.update_progress(progress)
                
                return '\n\n'.join(extracted_text)
                
        except Exception as e:
            logging.error(f"PDF processing failed: {e}", exc_info=True)
            raise