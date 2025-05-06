import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QPushButton, QLabel, QTextEdit, QProgressBar,
                            QMessageBox)
from PyQt6.QtCore import Qt
from .gui.wallet_scanner import WalletScanner

class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación de verificación de wallets Monero.
    Gestiona la interfaz gráfica y la interacción con el usuario.
    """
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Verificador de Monero")
        self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        title = QLabel("Verificador de Wallets Monero")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

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

        self.scanner = None

    def start_scanning(self) -> None:
        """
        Inicia o detiene el escaneo de wallets Monero.
        Muestra mensajes de error si ocurre alguna excepción.
        """
        if self.scanner is None or not self.scanner.isRunning():
            try:
                self.scanner = WalletScanner(test_mode=True)
                self.scanner.progress_updated.connect(self.update_progress)
                self.scanner.wallet_found.connect(self.add_wallet)
                self.scanner.error_occurred.connect(self.show_error)
                self.scanner.start()
                self.start_button.setText("Detener Escaneo")
                self.results_area.clear()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al iniciar el escaneo: {str(e)}")
        else:
            self.scanner.stop()
            self.start_button.setText("Iniciar Escaneo")

    def update_progress(self, value: int) -> None:
        """
        Actualiza la barra de progreso en la interfaz.

        Args:
            value (int): Porcentaje de progreso (0-100).
        """
        self.progress_bar.setValue(value)

    def add_wallet(self, wallet_info: str) -> None:
        """
        Añade la información de una wallet encontrada al área de resultados.

        Args:
            wallet_info (str): Texto con los detalles de la wallet encontrada.
        """
        self.results_area.append(wallet_info)

    def show_error(self, error_message: str) -> None:
        """
        Muestra un mensaje de error en la interfaz y lo añade al área de resultados.

        Args:
            error_message (str): Mensaje de error a mostrar.
        """
        self.results_area.append(f"Error: {error_message}")
        QMessageBox.warning(self, "Error", error_message)

def main() -> int:
    """
    Función principal de arranque de la aplicación.

    Returns:
        int: Código de salida de la aplicación.
    """
    """Función principal de la aplicación"""
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        return app.exec()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())