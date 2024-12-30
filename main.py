"""
Expapyrus: From physical images to digital text.
Author: Alejandro Domingo Agustí
Version: 1.0.8
"""

import logging
import tkinter as tk
from src.gui import ExpapyrusGUI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('expapyrus.log', encoding='utf-8')
    ]
)

def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = ExpapyrusGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()