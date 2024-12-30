"""
Expapyrus: From physical images to digital text.
A modern OCR tool for extracting text from PDFs.

Author: Alejandro Domingo Agustí
Version: 1.1.0
License: SOLO (Single Owner Licensing Option)
"""

import logging
from pathlib import Path
from typing import Dict, Any

# Version info
__version__ = '1.1.0'
__author__ = 'Your Name'
__email__ = 'your.email@example.com'
__license__ = 'MIT'

# Package metadata
metadata: Dict[str, Any] = {
    'name': 'Expapyrus',
    'version': __version__,
    'author': __author__,
    'author_email': __email__,
    'description': 'A modern OCR tool for extracting text from PDFs',
    'license': __license__,
    'repository': 'https://github.com/yourusername/expapyrus',
}

# Setup logging
def setup_logging() -> None:
    """Configure logging for the application."""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / 'expapyrus.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    
    logging.info(f"Initializing {metadata['name']} v{__version__}")

# Expose main classes and functions
from .config import OCRConfig
from .ocr_processor import PDFOCRExtractor
from .gui import ExpapyrusGUI

# Initialize package
setup_logging()

# Define what gets imported with 'from expapyrus import *'
__all__ = [
    'OCRConfig',
    'PDFOCRExtractor',
    'ExpapyrusGUI',
    '__version__',
    '__author__',
    '__email__',
    '__license__',
    'metadata'
]

# Optional: Package initialization code
def initialize_package() -> None:
    """Initialize package resources and verify dependencies."""
    try:
        # Verify critical directories exist
        directories = [
            Path('logs'),
            Path('output'),
            Path('temp')
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            logging.debug(f"Verified directory: {directory}")
        
        # Verify configuration files
        config_file = Path('settings.json')
        if not config_file.exists():
            from .constants import DEFAULT_SETTINGS
            import json
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_SETTINGS, f, indent=4)
            logging.info(f"Created default configuration file: {config_file}")
        
        # Additional initialization as needed
        logging.info("Package initialization completed successfully")
        
    except Exception as e:
        logging.error(f"Failed to initialize package: {e}")
        raise

# Run initialization
try:
    initialize_package()
except Exception as e:
    logging.error(f"Package initialization failed: {e}")

def get_version() -> str:
    """Return the current version of the package."""
    return __version__

def get_metadata() -> Dict[str, Any]:
    """Return package metadata."""
    return metadata.copy()

def verify_installation() -> bool:
    """
    Verify that all required components are properly installed.
    
    Returns:
        bool: True if all components are properly installed, False otherwise
    """
    try:
        # Verify Tesseract installation
        import pytesseract
        tesseract_version = pytesseract.get_tesseract_version()
        logging.info(f"Tesseract version: {tesseract_version}")
        
        # Verify Poppler installation
        poppler_path = Path(r'C:\Program Files\poppler-24.08.0\Library\bin')
        if not poppler_path.exists():
            raise FileNotFoundError(f"Poppler not found at: {poppler_path}")
        
        # Verify required directories
        required_dirs = ['logs', 'output', 'temp']
        for dir_name in required_dirs:
            if not Path(dir_name).exists():
                raise FileNotFoundError(f"Required directory not found: {dir_name}")
        
        logging.info("Installation verification completed successfully")
        return True
        
    except Exception as e:
        logging.error(f"Installation verification failed: {e}")
        return False

def cleanup() -> None:
    """Clean up temporary files and resources."""
    try:
        import shutil
        temp_dir = Path('temp')
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            temp_dir.mkdir()
        logging.info("Cleanup completed successfully")
    except Exception as e:
        logging.error(f"Cleanup failed: {e}")

# Register cleanup function to be called on exit
import atexit
atexit.register(cleanup)