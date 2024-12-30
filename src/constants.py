"""Constants module for the application."""

# Application Information
APP_TITLE = "Expapyrus"
APP_VERSION = "1.1.0"
WINDOW_SIZE = "800x600"

# OCR Configuration
DEFAULT_DPI = 300
SUPPORTED_LANGUAGES = ['eng', 'spa', 'cat', 'eng+spa', 'eng+cat', 'spa+cat']
OUTPUT_SUFFIX = "_extracted_text.txt"

# Default Settings
DEFAULT_SETTINGS = {
    'default_language': 'eng',
    'default_dpi': 300,
    'auto_save': True,
    'recent_files': [],
    'last_directory': None
}

# Theme Configuration
THEME_CONFIG = {
    'TButton': {
        'padding': 5,
        'font': ('Segoe UI', 9)
    },
    'Accent.TButton': {
        'padding': 5,
        'font': ('Segoe UI', 9, 'bold'),
        'background': '#007bff'
    },
    'TLabel': {
        'font': ('Segoe UI', 9)
    },
    'TLabelframe': {
        'padding': 5
    },
    'TEntry': {
        'padding': 5
    }
}

# File Handling
MAX_RECENT_FILES = 10
RECENT_FILES_FILE = 'recent_files.json'
SETTINGS_FILE = 'settings.json'