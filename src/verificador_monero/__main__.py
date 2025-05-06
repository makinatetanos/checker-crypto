"""
Punto de entrada principal de la aplicación.
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication

from .gui import MainWindow
from .utils import setup_logging

def main():
    """Función principal de la aplicación."""
    try:
        # Configurar logging
        setup_logging()
        
        # Crear y mostrar la ventana principal
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        
        # Ejecutar la aplicación
        return app.exec()
    except Exception as e:
        logging.error(f"Error al iniciar la aplicación: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main()) 