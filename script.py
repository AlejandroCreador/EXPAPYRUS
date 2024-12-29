"""
PDF OCR Text Extractor
A tool to extract and process text from PDF files using OCR technology.
Author: [Your Name]
Version: 1.0.1
"""

import os
import logging
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox

# Constants
DEFAULT_DPI = 300
SUPPORTED_LANGUAGES = 'eng+spa+cat'
PLACEHOLDER_TEXT = "[VACÍO POR TEXTO MANUSCRITO NO LEGIBLE]"
OUTPUT_SUFFIX = "_texto_extraido.txt"

@dataclass
class OCRConfig:
    """Configuration settings for OCR processing."""
    tesseract_path: str = r'C:\Program Files (x86)\Tesseract-OCR'
    dpi: int = DEFAULT_DPI
    languages: str = SUPPORTED_LANGUAGES

class LoggerSetup:
    """Configure and manage logging settings."""
    
    @staticmethod
    def configure() -> None:
        """Set up basic logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('pdf_ocr.log', encoding='utf-8')
            ]
        )

class TextProcessor:
    """Handle text processing and formatting operations."""
    
    @staticmethod
    def format_text(text: str) -> str:
        """Format extracted text according to specified rules."""
        if not text:
            return ""
            
        formatting_rules = [
            (r'\n{3,}', '\n\n'),              # Limit consecutive line breaks
            (r'\s+', ' '),                     # Remove excessive whitespace
            (r'\.{2,}', PLACEHOLDER_TEXT),     # Replace ellipsis
            (r'_{2,}', PLACEHOLDER_TEXT),      # Replace underscores
        ]
        
        formatted_text = text
        for pattern, replacement in formatting_rules:
            formatted_text = re.sub(pattern, replacement, formatted_text)
            
        return formatted_text.strip()

class PDFOCRExtractor:
    """Main class for PDF OCR text extraction."""
    
    def __init__(self, config: OCRConfig):
        """Initialize the PDF OCR extractor with configuration."""
        self.config = config
        self.temp_dir = Path(tempfile.mkdtemp())
        pytesseract.pytesseract.tesseract_cmd = config.tesseract_path
        self.text_processor = TextProcessor()
        
    def process_pdf(self, pdf_path: Path) -> Optional[str]:
        """Process PDF file and extract text."""
        try:
            images = self._convert_pdf_to_images(pdf_path)
            if not images:
                raise ValueError("No images extracted from PDF")
                
            extracted_text = self._process_images(images)
            return extracted_text
            
        except Exception as e:
            logging.error(f"Error processing PDF: {e}")
            return None
        finally:
            self._cleanup()
            
    def _convert_pdf_to_images(self, pdf_path: Path) -> List[Image.Image]:
        """Convert PDF pages to images."""
        logging.info(f"Converting PDF to images: {pdf_path}")
        try:
            images = convert_from_path(
                pdf_path,
                dpi=self.config.dpi,
                output_folder=self.temp_dir
            )
            logging.info(f"Converted {len(images)} pages")
            return images
        except Exception as e:
            logging.error(f"PDF conversion failed: {e}")
            return []
            
    def _process_images(self, images: List[Image.Image]) -> str:
        """Process images and extract text."""
        all_text = []
        for idx, image in enumerate(images, 1):
            logging.info(f"Processing page {idx}")
            try:
                text = pytesseract.image_to_string(
                    image,
                    lang=self.config.languages
                )
                formatted_text = self.text_processor.format_text(text)
                all_text.append(f"Página {idx}\n\n{formatted_text}")
            except Exception as e:
                logging.error(f"Error processing page {idx}: {e}")
                all_text.append(f"Página {idx}\n\n[ERROR DE PROCESAMIENTO]")
                
        return '\n\n'.join(all_text)
        
    def _cleanup(self) -> None:
        """Clean up temporary files."""
        try:
            for file in self.temp_dir.glob('*'):
                file.unlink()
            self.temp_dir.rmdir()
            logging.info("Temporary files cleaned up")
        except Exception as e:
            logging.error(f"Cleanup failed: {e}")

class FileHandler:
    """Handle file operations."""
    
    @staticmethod
    def save_text(text: str, output_path: Path) -> bool:
        """Save extracted text to file."""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(text, encoding='utf-8')
            logging.info(f"Text saved to: {output_path}")
            return True
        except Exception as e:
            logging.error(f"Failed to save text: {e}")
            return False

class GUI:
    """Handle GUI operations."""
    
    @staticmethod
    def select_pdf() -> Optional[Path]:
        """Show file dialog to select PDF."""
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        return Path(file_path) if file_path else None
        
    @staticmethod
    def show_message(title: str, message: str, error: bool = False) -> None:
        """Show message dialog."""
        if error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)

def main():
    """Main execution function."""
    LoggerSetup.configure()
    
    try:
        # Initialize configuration
        config = OCRConfig()
        
        # Select PDF file
        pdf_path = GUI.select_pdf()
        if not pdf_path:
            GUI.show_message("Información", "No se seleccionó ningún archivo.")
            return
            
        # Initialize extractor
        extractor = PDFOCRExtractor(config)
        
        # Process PDF
        extracted_text = extractor.process_pdf(pdf_path)
        if not extracted_text:
            raise ValueError("No se pudo extraer texto del PDF")
            
        # Save results
        output_path = pdf_path.parent / f"{pdf_path.stem}{OUTPUT_SUFFIX}"
        if FileHandler.save_text(extracted_text, output_path):
            GUI.show_message(
                "Proceso completado",
                f"El texto extraído se ha guardado en:\n{output_path}"
            )
        else:
            raise ValueError("Error al guardar el archivo")
            
    except Exception as e:
        logging.error(f"Application error: {e}")
        GUI.show_message("Error", str(e), error=True)

if __name__ == "__main__":
    main()