"""
Ventana principal de la aplicación.
"""

import logging
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                            QPushButton, QLabel, QTextEdit, QProgressBar,
                            QMessageBox)
from PyQt6.QtCore import Qt

from .wallet_scanner import WalletScanner

logger = logging.getLogger('verificador_monero.gui')

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        """Inicializa la ventana principal."""
        super().__init__()
        logger.info("Inicializando ventana principal")
        self.setWindowTitle("Verificador de Monero")
        self.setMinimumSize(800, 600)
        
        self._init_ui()
        self.scanner = None
        
    def _init_ui(self):
        """Inicializa los elementos de la interfaz."""
        try:
            logger.debug("Inicializando elementos de la interfaz")
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            # Título
            title = QLabel("Verificador de Wallets Monero")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
            layout.addWidget(title)

            # Botón de inicio/detención
            self.start_button = QPushButton("Iniciar Escaneo")
            self.start_button.clicked.connect(self.start_scanning)
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            layout.addWidget(self.start_button)

            # Barra de progreso
            self.progress_bar = QProgressBar()
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                }
            """)
            self.progress_bar.setValue(0)
            layout.addWidget(self.progress_bar)

            # Área de resultados
            self.results_area = QTextEdit()
            self.results_area.setReadOnly(True)
            self.results_area.setStyleSheet("""
                QTextEdit {
                    background-color: #f8f9fa;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 10px;
                    font-family: 'Consolas', monospace;
                }
            """)
            layout.addWidget(self.results_area)
            logger.debug("Elementos de la interfaz inicializados correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar la interfaz: {str(e)}")
            raise

    def start_scanning(self):
        """Inicia o detiene el escaneo de wallets."""
        try:
            if self.scanner is None or not self.scanner.isRunning():
                logger.info("Iniciando escaneo de wallets")
                self.scanner = WalletScanner(test_mode=True)
                self.scanner.progress_updated.connect(self.update_progress)
                self.scanner.wallet_found.connect(self.add_wallet)
                self.scanner.error_occurred.connect(self.show_error)
                self.scanner.start()
                self.start_button.setText("Detener Escaneo")
                self.results_area.clear()
            else:
                logger.info("Deteniendo escaneo de wallets")
                self.scanner.stop()
                self.start_button.setText("Iniciar Escaneo")
        except Exception as e:
            error_msg = f"Error al controlar el escaneo: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def update_progress(self, value: int):
        """Actualiza la barra de progreso."""
        try:
            logger.debug(f"Actualizando progreso: {value}%")
            self.progress_bar.setValue(value)
        except Exception as e:
            logger.error(f"Error al actualizar progreso: {str(e)}")

    def add_wallet(self, wallet_info: str):
        """Agrega información de una wallet encontrada."""
        try:
            logger.info("Wallet encontrada")
            self.results_area.append(wallet_info)
        except Exception as e:
            logger.error(f"Error al agregar wallet: {str(e)}")

    def show_error(self, error_message: str):
        """Muestra un mensaje de error."""
        try:
            logger.error(f"Error en el escaneo: {error_message}")
            self.results_area.append(f"Error: {error_message}")
            QMessageBox.warning(self, "Error", error_message)
        except Exception as e:
            logger.error(f"Error al mostrar mensaje de error: {str(e)}") 