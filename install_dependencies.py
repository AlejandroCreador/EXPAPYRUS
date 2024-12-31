"""Enhanced dependency installation script."""

import subprocess
import sys
import platform
from typing import List, Tuple, Dict
from enum import Enum
import os
from pathlib import Path
import json

class DependencyGroup(Enum):
    """Dependency group categories."""
    CORE = "Core Dependencies"
    GUI = "GUI Dependencies"
    BUILD = "Build Tools"
    DEV = "Development Tools"
    UTILS = "Utilities"
    SYSTEM = "System Integration"
    OPTIONAL = "Optional Dependencies"

class DependencyManager:
    """Manages project dependencies installation."""

    def __init__(self):
        self.dependencies: Dict[DependencyGroup, List[str]] = {
            DependencyGroup.CORE: [
                "pytesseract",
                "pdf2image",
                "PyPDF2",
                "pdfminer.six",
                "poppler-utils",
                "Pillow",
                "opencv-python",
                "numpy",
                "scikit-image"
            ],
            DependencyGroup.GUI: [
                "tk",
                "ttkthemes",
                "customtkinter",
                "darkdetect",
                "sv-ttk"
            ],
            DependencyGroup.BUILD: [
                "pyinstaller",
                "cx_Freeze",
                "wheel",
                "setuptools",
                "py2exe",
                "auto-py-to-exe"
            ],
            DependencyGroup.DEV: [
                "black",
                "pylint",
                "mypy",
                "pytest",
                "pytest-cov",
                "flake8",
                "autopep8",
                "isort"
            ],
            DependencyGroup.UTILS: [
                "python-dotenv",
                "pathlib",
                "typing-extensions",
                "colorama",
                "tqdm",
                "rich",
                "click",
                "pyyaml"
            ],
            DependencyGroup.SYSTEM: [
                "psutil",
                "watchdog"
            ],
            DependencyGroup.OPTIONAL: [
                "requests",
                "urllib3",
                "certifi",
                "loguru",
                "pyperclip"
            ]
        }

        # Windows-specific dependencies
        if platform.system() == "Windows":
            self.dependencies[DependencyGroup.SYSTEM].append("pywin32")

    def install_group(self, group: DependencyGroup) -> Tuple[bool, str]:
        """Install all dependencies in a group."""
        print(f"\nInstalling {group.value}...")
        success = True
        errors = []

        for dep in self.dependencies[group]:
            try:
                print(f"Installing {dep}...")
                subprocess.check_call([
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    dep
                ])
            except Exception as e:
                success = False
                errors.append(f"{dep}: {str(e)}")

        if success:
            return True, f"{group.value} installed successfully"
        return False, f"Errors installing {group.value}: {'; '.join(errors)}"

    def install_all(self) -> bool:
        """Install all dependencies."""
        print("Starting complete dependency installation...")
        
        success = True
        for group in DependencyGroup:
            ok, message = self.install_group(group)
            print(message)
            if not ok:
                success = False

        return success

    def verify_installation(self) -> Tuple[bool, List[str]]:
        """Verify all dependencies are installed correctly."""
        missing = []
        for group in self.dependencies.values():
            for dep in group:
                try:
                    __import__(dep.split('[')[0])
                except ImportError:
                    missing.append(dep)
        
        return len(missing) == 0, missing

def main():
    """Main installation process."""
    if sys.version_info < (3, 8):
        print("Python 3.8 or higher is required")
        sys.exit(1)

    manager = DependencyManager()
    
    print("=== Expapyrus Dependency Installation ===")
    
    if manager.install_all():
        print("\nAll dependencies installed successfully!")
        
        # Verify installation
        success, missing = manager.verify_installation()
        if not success:
            print("\nWarning: Some packages might not be installed correctly:")
            for pkg in missing:
                print(f"  - {pkg}")
            
        print("\nNext steps:")
        print("1. Verify Tesseract OCR installation")
        print("2. Verify Poppler installation")
        print("3. Run tests with 'pytest'")
        print("4. Try building the application")
    else:
        print("\nSome installations failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()