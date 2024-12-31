"""Build script for creating the executable."""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import PyInstaller.__main__

def clean_build_directories():
    """Clean build and dist directories."""
    directories = ['build', 'dist']
    for directory in directories:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Limpiado directorio {directory}")

def create_assets_directory():
    """Create assets directory if it doesn't exist."""
    assets_dir = Path('assets')
    assets_dir.mkdir(exist_ok=True)
    print("Directorio assets verificado")

def copy_dependencies():
    """Copy necessary dependency files."""
    try:
        # Create directories
        dist_dir = Path('dist/Expapyrus')
        dist_dir.mkdir(parents=True, exist_ok=True)

        # Copy configuration files if they exist
        files_to_copy = ['settings.json', 'config.ini']
        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy(file, dist_dir)
                print(f"Copiado archivo {file}")
            else:
                print(f"Advertencia: No se encuentra {file}")

        # Copy assets directory if it exists
        if os.path.exists('assets'):
            shutil.copytree('assets', dist_dir / 'assets', dirs_exist_ok=True)
            print("Copiado directorio assets")

    except Exception as e:
        print(f"Error copiando dependencias: {e}")
        raise

def build_executable():
    """Build the executable using PyInstaller."""
    try:
        PyInstaller.__main__.run([
            'main.py',
            '--name=Expapyrus',
            '--windowed',
            '--onefile',
            '--icon=assets/icon.ico',
            '--add-data=src;src',
            '--clean',
            '--noconfirm'
        ])
        print("Ejecutable creado exitosamente")
    except Exception as e:
        print(f"Error durante la construcción: {e}")
        raise

def main():
    """Main build process."""
    try:
        print("Iniciando proceso de construcción...")
        
        # Clean previous builds
        clean_build_directories()
        
        # Setup directories
        create_assets_directory()
        
        # Build executable
        build_executable()
        
        # Copy additional files
        copy_dependencies()
        
        print("Proceso de construcción completado exitosamente")
        return 0
        
    except Exception as e:
        print(f"Error durante la construcción: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())