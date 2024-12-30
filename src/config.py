"""Configuration module for OCR settings."""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Union

class OCRConfig:
    """Configuration class for OCR settings."""

    def __init__(self) -> None:
        """Initialize OCR configuration with default values."""
        self.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        self.tessdata_dir = r"C:\Program Files\Tesseract-OCR\tessdata"
        self.languages = ["eng"]
        self.dpi = 300
        self.config_file = "ocr_config.json"
        
        self._verify_tesseract()
        self._load_config()

    def _verify_tesseract(self) -> None:
        """Verify Tesseract installation and paths."""
        if not os.path.exists(self.tesseract_cmd):
            raise FileNotFoundError(f"Tesseract executable not found at: {self.tesseract_cmd}")
        if not os.path.exists(self.tessdata_dir):
            raise FileNotFoundError(f"Tessdata directory not found at: {self.tessdata_dir}")
        logging.info(f"Tesseract command: {self.tesseract_cmd}")
        logging.info(f"Path to tessdata: {self.tessdata_dir}")

    def _load_config(self) -> None:
        """Load configuration from file if exists."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self._update_config(config)
                logging.info("Configuration loaded successfully")
            except Exception as e:
                logging.error(f"Error loading configuration: {e}")

    def _update_config(self, config: Dict[str, Any]) -> None:
        """Update configuration with provided values."""
        if 'tesseract_cmd' in config:
            self.tesseract_cmd = config['tesseract_cmd']
        if 'tessdata_dir' in config:
            self.tessdata_dir = config['tessdata_dir']
        if 'languages' in config:
            self.set_languages(config['languages'])
        if 'dpi' in config:
            self.dpi = int(config['dpi'])

    def save_config(self) -> None:
        """Save current configuration to file."""
        config = {
            'tesseract_cmd': self.tesseract_cmd,
            'tessdata_dir': self.tessdata_dir,
            'languages': self.languages,
            'dpi': self.dpi
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            logging.info("Configuration saved successfully")
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")

    def set_languages(self, languages: Union[str, List[str]]) -> None:
        """
        Set OCR languages.
        
        Args:
            languages: String of language codes separated by '+' or list of language codes
        """
        if isinstance(languages, str):
            self.languages = [lang.strip() for lang in languages.split('+')]
        elif isinstance(languages, list):
            self.languages = languages
        else:
            raise ValueError("Languages must be a string or list of language codes")
        
        # Verify language files exist
        for lang in self.languages:
            lang_file = os.path.join(self.tessdata_dir, f"{lang}.traineddata")
            if not os.path.exists(lang_file):
                raise FileNotFoundError(f"Language file not found: {lang_file}")
        
        logging.info(f"Languages set to: {self.languages}")

    def get_languages_string(self) -> str:
        """Get languages as '+' separated string for Tesseract."""
        return '+'.join(self.languages)

    def set_dpi(self, dpi: int) -> None:
        """
        Set OCR DPI value.
        
        Args:
            dpi: Integer value for DPI (must be positive)
        """
        if not isinstance(dpi, int) or dpi <= 0:
            raise ValueError("DPI must be a positive integer")
        self.dpi = dpi
        logging.info(f"DPI set to: {self.dpi}")