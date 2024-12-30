"""Settings management module."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class Settings:
    """Manages application settings."""

    def __init__(self, settings_file: str):
        self.settings_file = Path(settings_file)
        self.settings: Dict[str, Any] = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._get_default_settings()
        return self._get_default_settings()

    def save_settings(self):
        """Save current settings to file."""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        """Set a setting value."""
        self.settings[key] = value
        self.save_settings()

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings."""
        return {
            'last_directory': str(Path.home()),
            'default_language': 'eng',
            'default_dpi': 300,
            'recent_files': [],
            'theme': 'default',
            'auto_save': True,
            'output_directory': str(Path.home() / 'Expapyrus Output')
        }