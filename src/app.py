import sys
import random
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QTextEdit, QMessageBox,
    QLineEdit, QSpinBox, QCheckBox, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPalette, QColor

from .config import MoneroConfig
from .wallet import WalletManager, MoneroWallet
from .utils import (
    generate_seed, validate_monero_address, format_balance,
    format_timestamp, setup_directories
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScannerThread(QThread):
    progress_updated = pyqtSignal(float)
    wallet_found = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, config: MoneroConfig, wallet_manager: WalletManager) -> None:
        super().__init__()
        self.config = config
        self.wallet_manager = wallet_manager
        self.is_running = False
        self.attempts = 0

    def run(self) -> None:
        self.is_running = True
        while self.is_running and self.attempts < self.config.max_attempts:
            try:
                seed = generate_seed()
                address = f"4{seed[:94]}"
                if self.config.test_mode:
                    balance = 0.0 if random.random() < 0.99 else random.uniform(0.1, 100.0)
                else:
                    balance = self.wallet_manager.check_balance_sync(
                        address,
                        self.config.get_rpc_url()
                    ) or 0.0
                if balance > 0:
                    wallet = MoneroWallet(
                        address=address,
                        balance=balance,
                        is_lost=True,
                        last_checked=datetime.now()
                    )
                    self.wallet_manager.add_wallet_sync(wallet)
                    self.wallet_found.emit(wallet)
                self.attempts += 1
                progress = (self.attempts / self.config.max_attempts) * 100
                self.progress_updated.emit(progress)
                self.msleep(int(self.config.scan_interval_ms))
            except Exception as e:
                logger.error(f"Error en escaneo: {e}")
                self.error_occurred.emit(str(e))
                self.msleep(1000)
        self.finished.emit()

    def stop(self) -> None:
        self.is_running = False

class MoneroApp(QMainWindow):
    def __init__(self, config: MoneroConfig) -> None:
        super().__init__()
        self.config: MoneroConfig = config
        self.wallet_manager: WalletManager = WalletManager(config.data_dir)
        self.scanner: Optional[ScannerThread] = None
        self.dark_mode: bool = True
        self.setup_ui()
        self.setup_directories()

    def setup_ui(self) -> None:
        self.setWindowTitle("Monero Wallet Scanner")
        self.setMinimumSize(800, 600)

        # Widget principal
        main_widget: QWidget = QWidget()
        self.setCentralWidget(main_widget)
        layout: QVBoxLayout = QVBoxLayout(main_widget)

        # Configuración
        config_group: QGroupBox = QGroupBox("Configuración")
        config_layout: QFormLayout = QFormLayout()
        
        self.rpc_host_input: QLineEdit = QLineEdit(self.config.rpc_host)
        self.rpc_port_input: QLineEdit = QLineEdit(self.config.rpc_port)
        self.test_mode_check: QCheckBox = QCheckBox()
        self.test_mode_check.setChecked(self.config.test_mode)
        self.max_threads_input: QSpinBox = QSpinBox()
        self.max_threads_input.setRange(1, 32)
        self.max_threads_input.setValue(self.config.max_threads)
        self.scan_interval_input: QSpinBox = QSpinBox()
        self.scan_interval_input.setRange(100, 10000)
        self.scan_interval_input.setValue(self.config.scan_interval_ms)
        self.max_attempts_input: QSpinBox = QSpinBox()
        self.max_attempts_input.setRange(1, 1000000)
        self.max_attempts_input.setValue(self.config.max_attempts)

        config_layout.addRow("RPC Host:", self.rpc_host_input)
        config_layout.addRow("RPC Port:", self.rpc_port_input)
        config_layout.addRow("Modo Test:", self.test_mode_check)
        config_layout.addRow("Máx. Hilos:", self.max_threads_input)
        config_layout.addRow("Intervalo (ms):", self.scan_interval_input)
        config_layout.addRow("Máx. Intentos:", self.max_attempts_input)
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # Controles
        controls_layout: QHBoxLayout = QHBoxLayout()
        self.start_button: QPushButton = QPushButton("Iniciar Escaneo")
        self.start_button.clicked.connect(self.toggle_scanning)
        self.dark_mode_button: QPushButton = QPushButton("Cambiar Tema")
        self.dark_mode_button.clicked.connect(self.toggle_theme)
        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.dark_mode_button)
        layout.addLayout(controls_layout)

        # Barra de progreso
        self.progress_bar: QProgressBar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Resultados
        results_group: QGroupBox = QGroupBox("Resultados")
        results_layout: QVBoxLayout = QVBoxLayout()
        self.results_text: QTextEdit = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        # Estadísticas
        stats_group: QGroupBox = QGroupBox("Estadísticas")
        stats_layout: QFormLayout = QFormLayout()
        self.total_attempts_label: QLabel = QLabel("0")
        self.wallets_found_label: QLabel = QLabel("0")
        self.total_balance_label: QLabel = QLabel("0.000000000000 XMR")
        stats_layout.addRow("Intentos Totales:", self.total_attempts_label)
        stats_layout.addRow("Wallets Encontradas:", self.wallets_found_label)
        stats_layout.addRow("Balance Total:", self.total_balance_label)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        self.apply_theme()

    def setup_directories(self) -> None:
        setup_directories()

    def toggle_scanning(self) -> None:
        if self.scanner and self.scanner.is_running:
            self.scanner.stop()
            self.start_button.setText("Iniciar Escaneo")
        else:
            self.start_scanning()
            self.start_button.setText("Detener Escaneo")

    def start_scanning(self) -> None:
        self.config.rpc_host = self.rpc_host_input.text()
        self.config.rpc_port = self.rpc_port_input.text()
        self.config.test_mode = self.test_mode_check.isChecked()
        self.config.max_threads = self.max_threads_input.value()
        self.config.scan_interval_ms = self.scan_interval_input.value()
        self.config.max_attempts = self.max_attempts_input.value()

        if not self.config.validate():
            QMessageBox.critical(self, "Error", "Configuración inválida")
            return

        self.scanner = ScannerThread(self.config, self.wallet_manager)
        self.scanner.progress_updated.connect(self.update_progress)
        self.scanner.wallet_found.connect(self.add_wallet_result)
        self.scanner.error_occurred.connect(self.show_error)
        self.scanner.finished.connect(self.scanning_finished)
        self.scanner.start()

    def update_progress(self, value: float) -> None:
        self.progress_bar.setValue(int(value))

    def add_wallet_result(self, wallet: MoneroWallet) -> None:
        self.results_text.append(
            f"Wallet encontrada:\n"
            f"Dirección: {wallet.address}\n"
            f"Balance: {format_balance(wallet.balance)}\n"
            f"Última verificación: {format_timestamp(int(wallet.last_checked.timestamp()))}\n"
            f"{'='*50}\n"
        )
        self.update_stats()

    def show_error(self, error: str) -> None:
        self.results_text.append(f"Error: {error}\n")

    def scanning_finished(self) -> None:
        self.start_button.setText("Iniciar Escaneo")
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "Completado", "Escaneo finalizado")

    def update_stats(self) -> None:
        wallets = asyncio.run(self.wallet_manager.get_all_wallets())
        total_balance = sum(w.balance for w in wallets)
        self.total_attempts_label.setText(str(self.scanner.attempts if self.scanner else 0))
        self.wallets_found_label.setText(str(len(wallets)))
        self.total_balance_label.setText(format_balance(total_balance))

    def toggle_theme(self) -> None:
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self) -> None:
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #3b3b3b;
                    border: 1px solid #555555;
                    padding: 5px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #4b4b4b;
                }
                QLineEdit, QSpinBox, QTextEdit {
                    background-color: #3b3b3b;
                    border: 1px solid #555555;
                    color: #ffffff;
                }
                QGroupBox {
                    border: 1px solid #555555;
                    margin-top: 1ex;
                }
                QGroupBox::title {
                    color: #ffffff;
                }
                QProgressBar {
                    border: 1px solid #555555;
                    background-color: #3b3b3b;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4b4b4b;
                }
            """)
        else:
            self.setStyleSheet("")

def main() -> None:
    app = QApplication(sys.argv)
    config = MoneroConfig.load_config()
    window = MoneroApp(config)
    window.show()
    sys.exit(app.exec()) 