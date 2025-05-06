import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import sys
print('[DEBUG] import sys OK')
import os
print('[DEBUG] import os OK')
from typing import Optional
print('[DEBUG] import typing OK')
from wallet import MoneroWallet
print('[DEBUG] import MoneroWallet OK')
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QTextEdit, QProgressBar, QMessageBox
)
print('[DEBUG] import PyQt6.QtWidgets OK')
from PyQt6.QtCore import Qt
print('[DEBUG] import PyQt6.QtCore OK')
import requests
print('[DEBUG] import requests OK')
from dotenv import load_dotenv
print('[DEBUG] import dotenv OK')
from verificador_monero.gui.wallet_scanner import WalletScanner
print('[DEBUG] import WalletScanner OK')
from verificador_monero.monero_handler import MoneroHandler
print('[DEBUG] import MoneroHandler OK')
def check_balance_sync(self, address: str, rpc_url: str) -> Optional[float]:
    # Implementación usando requests en vez de aiohttp
    try:
        import requests
        response = requests.post(rpc_url, json={
            "jsonrpc": "2.0",
            "id": "1",
            "method": "get_balance",
            "params": {"address": address}
        })
        if response.status_code == 200:
            data = response.json()
            return float(data.get('result', {}).get('balance', 0)) / 1e12
    except Exception as e:
        logger.error(f"Error checking balance: {e}")
    return None

def add_wallet_sync(self, wallet: MoneroWallet) -> bool:
    try:
        if wallet.address in self._wallets:
            return False
        self._wallets[wallet.address] = wallet
        self._save_wallets_sync()
        return True
    except Exception as e:
        logger.error(f"Error adding wallet: {e}")
        return False

def _save_wallets_sync(self):
    try:
        data = {
            addr: {
                'address': w.address,
                'balance': w.balance,
                'is_lost': w.is_lost,
                'last_checked': w.last_checked.isoformat() if w.last_checked else None,
                'private_key': w.private_key
            }
            for addr, w in self._wallets.items()
        }
        json_data = json.dumps(data)
        if self.encryption_key:
            from cryptography.fernet import Fernet
            fernet = Fernet(self.encryption_key.encode())
            json_data = fernet.encrypt(json_data.encode()).decode()
        with open(self.wallets_file, 'w') as f:
            f.write(json_data)
    except Exception as e:
        logger.error(f"Error saving wallets: {e}")

class MainWindow(QMainWindow):
    def logout(self):
        # Permite que la acción de menú funcione sin error
        if hasattr(self, '_logout_callback'):
            self._logout_callback()
        elif hasattr(self, 'logout_callback'):
            self.logout_callback()
        elif hasattr(self, 'logout_func'):
            self.logout_func()
        elif hasattr(self, 'logout_action'):
            self.logout_action()
        elif hasattr(self, 'logout_lambda'):
            self.logout_lambda()
        # Si se asigna window.logout en main(), también funcionará
        elif hasattr(self, 'logout') and callable(getattr(self, 'logout')):
            getattr(self, 'logout')()
        # Si no hay callback, simplemente no hace nada
        else:
            pass

    def show_account_info(self):
        # Permite que la acción de menú funcione sin error
        if hasattr(self, '_show_account_info_callback'):
            self._show_account_info_callback()
        elif hasattr(self, 'show_account_info_callback'):
            self.show_account_info_callback()
        elif hasattr(self, 'show_account_info_func'):
            self.show_account_info_func()
        elif hasattr(self, 'show_account_info_action'):
            self.show_account_info_action()
        elif hasattr(self, 'show_account_info_lambda'):
            self.show_account_info_lambda()
        # Si se asigna window.show_account_info en main(), también funcionará
        elif hasattr(self, 'show_account_info') and callable(getattr(self, 'show_account_info')):
            getattr(self, 'show_account_info')()
        else:
            pass

    def show_historial(self):
        # Permite que la acción de menú funcione sin error
        if hasattr(self, '_show_historial_callback'):
            self._show_historial_callback()
        elif hasattr(self, 'show_historial_callback'):
            self.show_historial_callback()
        elif hasattr(self, 'show_historial_func'):
            self.show_historial_func()
        elif hasattr(self, 'show_historial_action'):
            self.show_historial_action()
        elif hasattr(self, 'show_historial_lambda'):
            self.show_historial_lambda()
        # Si se asigna window.show_historial en main(), también funcionará
        elif hasattr(self, 'show_historial') and callable(getattr(self, 'show_historial')):
            getattr(self, 'show_historial')()
        else:
            pass
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr('app_title'))
        self.setMinimumSize(900, 650)

        # --- Barra de menú ---
        menubar = self.menuBar()
        lang_menu = menubar.addMenu(tr('change_lang'))
        lang_es = lang_menu.addAction(tr('spanish'))
        lang_en = lang_menu.addAction(tr('english'))
        lang_es.triggered.connect(lambda: self.set_language('es'))
        lang_en.triggered.connect(lambda: self.set_language('en'))
        account_menu = menubar.addMenu(tr('account'))
        theme_menu = menubar.addMenu(tr('menu_theme'))
        help_menu = menubar.addMenu(tr('menu_help'))

        self.action_logout = account_menu.addAction("Cerrar sesión")
        self.action_logout.triggered.connect(self.logout)
        self.action_account_info = account_menu.addAction("Información de cuenta")
        self.action_account_info.triggered.connect(self.show_account_info)
        self.action_historial = account_menu.addAction(tr('history'))
        self.action_historial.triggered.connect(self.show_historial)
        self.action_change_pwd = account_menu.addAction(tr('change_password') if 'change_password' in LANGUAGES[CURRENT_LANG[0]] else 'Cambiar contraseña')
        self.action_change_pwd.triggered.connect(self.change_password)

        self.action_theme_dark = theme_menu.addAction("Oscuro")
        self.action_theme_light = theme_menu.addAction("Claro")
        self.action_theme_dark.triggered.connect(self.set_dark_theme)
        self.action_theme_light.triggered.connect(self.set_light_theme)
        help_menu.addAction("Acerca de").triggered.connect(self.show_about)

        # --- Widget central y layout principal ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(14)
        layout.setContentsMargins(16, 16, 16, 16)

        # Título
        title = QLabel(tr('app_title'))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 27px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

        # Estado de usuario/licencia
        self.license_status = QLabel(tr('license_status_checking'))
        self.license_status.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.license_status.setStyleSheet("color: #FFA726; font-size: 13px; font-weight: bold;")
        layout.addWidget(self.license_status)

        # Estado de conexión RPC
        self.rpc_status = QLabel(tr('rpc_status_disconnected'))
        self.rpc_status.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.rpc_status.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.rpc_status)

        # Botones principales
        btn_layout = QVBoxLayout()
        self.start_button = QPushButton(tr('start_scan'))
        self.start_button.clicked.connect(self.start_scanning)
        self.start_button.setToolTip(tr('start_scan'))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_layout.addWidget(self.start_button)

        self.clear_button = QPushButton(tr('clear_results'))
        self.clear_button.clicked.connect(self.clear_results)
        self.clear_button.setToolTip(tr('clear_results'))
        btn_layout.addWidget(self.clear_button)

        self.export_button = QPushButton(tr('export_csv'))
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setToolTip(tr('export_csv'))
        btn_layout.addWidget(self.export_button)

        self.buy_button = QPushButton(tr('buy_license'))
        self.buy_button.clicked.connect(self.on_buy_license)
        self.buy_button.setToolTip(tr('buy_license'))
        btn_layout.addWidget(self.buy_button)

        layout.addLayout(btn_layout)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                font-size: 15px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)

        # Área de resultados
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setStyleSheet("""
            QTextEdit {
                background-color: #252525;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 14px;
            }
        """)
        self.results_area.setToolTip(tr('scan_results'))
        layout.addWidget(self.results_area)

        # Inicializar scanner y estado
        self.scanner = None
        self.wallets_encontradas = []
        self.set_dark_theme()
        self.update_rpc_status()

    def set_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #181818; }
            QLabel { color: #e0e0e0; }
            QMenuBar { background-color: #232323; color: #e0e0e0; }
            QMenuBar::item:selected { background: #444; }
            QMenu { background-color: #232323; color: #e0e0e0; }
            QMenu::item:selected { background: #444; }
            QPushButton { background-color: #333; color: #fff; }
            QPushButton:hover { background-color: #444; }
            QProgressBar { color: #fff; }
        """)

    def set_light_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
            QLabel { color: #222; }
            QMenuBar { background-color: #e0e0e0; color: #222; }
            QMenuBar::item:selected { background: #ccc; }
            QMenu { background-color: #e0e0e0; color: #222; }
            QMenu::item:selected { background: #ccc; }
            QPushButton { background-color: #fff; color: #222; }
            QPushButton:hover { background-color: #eee; }
            QProgressBar { color: #222; }
        """)

    def set_language(self, lang_code):
        CURRENT_LANG[0] = lang_code
        self.refresh_ui_texts()

    def refresh_ui_texts(self):
        self.setWindowTitle(tr('app_title'))
        self.license_status.setText(tr('license_status_checking'))
        self.rpc_status.setText(tr('rpc_status_disconnected'))
        self.start_button.setText(tr('start_scan'))
        self.start_button.setToolTip(tr('start_scan'))
        self.clear_button.setText(tr('clear_results'))
        self.clear_button.setToolTip(tr('clear_results'))
        self.export_button.setText(tr('export_csv'))
        self.export_button.setToolTip(tr('export_csv'))
        self.buy_button.setText(tr('buy_license'))
        self.buy_button.setToolTip(tr('buy_license'))
        self.results_area.setToolTip(tr('scan_results'))
        if hasattr(self, 'action_change_pwd'):
            self.action_change_pwd.setText(tr('change_password') if 'change_password' in LANGUAGES[CURRENT_LANG[0]] else 'Cambiar contraseña')
        self.update_license_status()

    def show_about(self):
        QMessageBox.information(self, tr('about'), tr('about_text'))

    def on_buy_license(self):
        if hasattr(self, 'prompt_payment'):
            self.prompt_payment()

    def update_license_status(self):
        license_data = getattr(self, 'license_data', None)
        if not license_data:
            self.license_status.setText(tr('license_status_checking'))
            self.license_status.setStyleSheet("color: #FFA726; font-size: 13px; font-weight: bold;")
            return
        if license_data.get("licensed", False):
            self.license_status.setText(tr('license_status_pro', user=license_data.get('user','')))
            self.license_status.setStyleSheet("color: #4CAF50; font-size: 13px; font-weight: bold;")
            self.buy_button.setVisible(False)
        else:
            usage = license_data.get("usage", 0)
            self.license_status.setText(tr('license_status_free', usage=usage, limit=USAGE_LIMIT_FREE))
            self.license_status.setStyleSheet("color: #FFA726; font-size: 13px; font-weight: bold;")
            self.buy_button.setVisible(True)
        # Actualizar info de cuenta si está abierta
        if hasattr(self, 'account_info_dialog') and self.account_info_dialog and self.account_info_dialog.isVisible():
            self.show_account_info()

    def change_password(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
        dialog = QDialog(self)
        dialog.setWindowTitle(tr('change_password') if 'change_password' in LANGUAGES[CURRENT_LANG[0]] else 'Cambiar contraseña')
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(tr('current_password') if 'current_password' in LANGUAGES[CURRENT_LANG[0]] else 'Contraseña actual:'))
        old_pwd = QLineEdit()
        old_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(old_pwd)
        layout.addWidget(QLabel(tr('new_password') if 'new_password' in LANGUAGES[CURRENT_LANG[0]] else 'Nueva contraseña:'))
        new_pwd = QLineEdit()
        new_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(new_pwd)
        btn = QPushButton(tr('change_password') if 'change_password' in LANGUAGES[CURRENT_LANG[0]] else 'Cambiar contraseña')
        layout.addWidget(btn)
        def do_change():
            user, real_pwd = self.get_user_pwd()
            if old_pwd.text() != real_pwd:
                QMessageBox.critical(dialog, tr('change_password') if 'change_password' in LANGUAGES[CURRENT_LANG[0]] else 'Cambiar contraseña', tr('wrong_password') if 'wrong_password' in LANGUAGES[CURRENT_LANG[0]] else 'Contraseña incorrecta.')
                return
            if not new_pwd.text():
                QMessageBox.warning(dialog, tr('change_password') if 'change_password' in LANGUAGES[CURRENT_LANG[0]] else 'Cambiar contraseña', tr('new_password_required') if 'new_password_required' in LANGUAGES[CURRENT_LANG[0]] else 'Debes ingresar una nueva contraseña.')
                return
            # Rotar clave del historial
            historial = load_historial(user, real_pwd)
            save_historial(user, new_pwd.text(), historial)
            # Actualizar licencia
            lic = self.license_data
            lic['user_hash'] = hash_user_pwd(user, new_pwd.text())
            save_license(lic)
            self.get_user_pwd = lambda: (user, new_pwd.text())
            QMessageBox.information(dialog, tr('change_password') if 'change_password' in LANGUAGES[CURRENT_LANG[0]] else 'Cambiar contraseña', tr('password_changed') if 'password_changed' in LANGUAGES[CURRENT_LANG[0]] else 'Contraseña cambiada correctamente.')
            dialog.accept()
        btn.clicked.connect(do_change)
        dialog.setLayout(layout)
        dialog.exec()

    def clear_results(self):
        self.results_area.clear()
        self.wallets_encontradas = []
        self.results_area.append('<span style="color:#888;">Área de resultados limpia.</span>')

    def export_results(self):
        if not self.wallets_encontradas:
            QMessageBox.warning(self, "Exportar", "No hay resultados para exportar.")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar como", "wallets.csv", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Dirección", "Balance", "Seed"])
                for wallet in self.wallets_encontradas:
                    writer.writerow(wallet)
            QMessageBox.information(self, "Exportar", f"Resultados exportados a {file_path}")

    def update_rpc_status(self):
        # Simulación de estado de conexión RPC
        try:
            # Aquí podrías hacer una petición real al nodo RPC
            self.rpc_status.setText("Estado RPC: Conectado")
            self.rpc_status.setStyleSheet("color: #4CAF50; font-size: 12px;")
        except Exception:
            self.rpc_status.setText("Estado RPC: No conectado")
            self.rpc_status.setStyleSheet("color: #e53935; font-size: 12px;")

    def start_scanning(self):
        print('[DEBUG] start_scanning llamado')
        # --- Restricción de uso para usuarios gratuitos ---
        license_data = getattr(self, 'license_data', None)
        print('[DEBUG] Revisando licencia y uso')
        if license_data and not license_data.get("licensed", False):
            usage = license_data.get("usage", 0)
            print('[DEBUG] Uso actual:', usage)
            if usage >= USAGE_LIMIT_FREE:
                print('[DEBUG] Límite de uso gratuito alcanzado')
                QMessageBox.warning(self, "Límite alcanzado",
                    f"Has alcanzado el límite gratuito de {USAGE_LIMIT_FREE} escaneos.\n\nActualiza a PRO para uso ilimitado.")
                self.buy_button.setStyleSheet("background-color: #FFA726; color: #222; font-weight: bold;")
                return
            else:
                # Incrementar contador de uso
                if hasattr(self, 'increment_usage'):
                    new_usage = self.increment_usage(self)
                    print('[DEBUG] Uso incrementado:', new_usage)
                    self.update_license_status()
        print('[DEBUG] Estado del scanner:', self.scanner, self.scanner is None or not (hasattr(self.scanner, 'isRunning') and self.scanner.isRunning()))
        if self.scanner is None or not self.scanner.isRunning():
            try:
                print('[DEBUG] Inicializando y arrancando WalletScanner')
                self.scanner = WalletScanner()
                self.scanner.progress_updated.connect(self.update_progress)
                self.scanner.wallet_found.connect(self.add_wallet)
                self.scanner.error_occurred.connect(self.show_error)
                self.scanner.start()
                self.start_button.setText("Detener Escaneo")
                self.results_area.clear()
            except Exception as e:
                print('[DEBUG] Error al iniciar el escaneo:', str(e))
                QMessageBox.critical(self, "Error", f"Error al iniciar el escaneo: {str(e)}")
        else:
            self.scanner.stop()
            self.start_button.setText("Iniciar Escaneo")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def add_wallet(self, wallet_info):
        # Mensaje de éxito resaltado
        self.results_area.append(f'<span style="color:#4CAF50;font-weight:bold;">{wallet_info}</span>')
        # --- Guardar en historial cifrado solo si tiene balance positivo ---
        try:
            # Parsear dirección, balance y seed del string wallet_info
            lines = wallet_info.split('\n')
            if len(lines) >= 4:
                addr = lines[1].split(':',1)[-1].strip()
                balance = float(lines[2].split(':',1)[-1].replace('XMR','').strip())
                seed = lines[3].split(':',1)[-1].strip()
                if balance > 0:
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    entry = {"address": addr, "balance": balance, "seed": seed, "datetime": now}
                    lic = getattr(self, 'license_data', None)
                    user = lic.get('user') if lic else None
                    pwd = None
                    if hasattr(self, 'get_user_pwd'):
                        user, pwd = self.get_user_pwd()
                    if user and pwd:
                        historial = load_historial(user, pwd)
                        historial.append(entry)
                        save_historial(user, pwd, historial)
        except Exception as e:
            pass

    def show_error(self, error_message):
        # Mensaje de error resaltado
        self.results_area.append(f'<span style="color:#e53935;font-weight:bold;">Error: {error_message}</span>')
        QMessageBox.warning(self, "Error", error_message)

from PyQt6.QtWidgets import QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QFileDialog
import json
import hashlib
from datetime import datetime
from cryptography.fernet import Fernet

# --- Internacionalización ---
LANGUAGES = {
    'es': {
        'app_title': 'Verificador de Wallets Monero',
        'login_title': 'Acceso a Checker Crypto',
        'user': 'Usuario',
        'password': 'Contraseña',
        'login': 'Iniciar sesión',
        'register': 'Registrar',
        'login_required': 'Usuario y contraseña requeridos.',
        'login_failed': 'Usuario o contraseña incorrectos.',
        'register_success': 'Usuario registrado. Acceso en modo gratuito.',
        'license_status_free': 'Licencia: Gratuita ({usage}/{limit} escaneos)',
        'license_status_pro': 'Licencia: PRO (usuario: {user})',
        'license_status_checking': 'Licencia: Consultando...',
        'rpc_status_connected': 'Estado RPC: Conectado',
        'rpc_status_disconnected': 'Estado RPC: No conectado',
        'start_scan': 'Iniciar Escaneo',
        'stop_scan': 'Detener Escaneo',
        'clear_results': 'Limpiar Resultados',
        'export_csv': 'Exportar a CSV',
        'buy_license': 'Adquirir Licencia PRO',
        'account': 'Cuenta',
        'logout': 'Cerrar sesión',
        'account_info': 'Información de cuenta',
        'scan_limit_reached': 'Has alcanzado el límite gratuito de {limit} escaneos.\n\nActualiza a PRO para uso ilimitado.',
        'about': 'Acerca de',
        'about_text': 'Verificador de Wallets Monero\nVersión mejorada\nmkttns',
        'show_hide_seeds': 'Mostrar/ocultar seeds',
        'export_history': 'Exportar historial a CSV',
        'privacy_warning': '¿Seguro que quieres mostrar las seeds? Son extremadamente sensibles.',
        'export_warning': '¿Exportar seeds en texto plano? ¡Riesgo extremo!\nAsegúrate de proteger el archivo.',
        'export_done': 'Historial exportado. Protege el archivo con extremo cuidado.',
        'no_wallets': 'Sin wallets con balance positivo en el historial.',
        'results_cleared': 'Área de resultados limpia.',
        'menu_theme': 'Tema',
        'theme_dark': 'Oscuro',
        'theme_light': 'Claro',
        'menu_help': 'Ayuda',
        'history': 'Historial de wallets',
        'scan_results': 'Aquí aparecerán los resultados del escaneo y los mensajes de error',
        'export_no_results': 'No hay resultados para exportar.',
        'login_exit': 'Salir',
        'change_lang': 'Idioma',
        'spanish': 'Español',
        'english': 'Inglés',
    },
    'en': {
        'app_title': 'Monero Wallet Checker',
        'login_title': 'Checker Crypto Login',
        'user': 'User',
        'password': 'Password',
        'login': 'Login',
        'register': 'Register',
        'login_required': 'Username and password required.',
        'login_failed': 'Incorrect username or password.',
        'register_success': 'User registered. Free mode access.',
        'license_status_free': 'License: Free ({usage}/{limit} scans)',
        'license_status_pro': 'License: PRO (user: {user})',
        'license_status_checking': 'License: Checking...',
        'rpc_status_connected': 'RPC status: Connected',
        'rpc_status_disconnected': 'RPC status: Not connected',
        'start_scan': 'Start Scan',
        'stop_scan': 'Stop Scan',
        'clear_results': 'Clear Results',
        'export_csv': 'Export to CSV',
        'buy_license': 'Buy PRO License',
        'account': 'Account',
        'logout': 'Logout',
        'account_info': 'Account Info',
        'scan_limit_reached': 'You have reached the free scan limit of {limit}.\n\nUpgrade to PRO for unlimited use.',
        'about': 'About',
        'about_text': 'Monero Wallet Checker\nEnhanced version\nDeveloped by Abel',
        'show_hide_seeds': 'Show/hide seeds',
        'export_history': 'Export history to CSV',
        'privacy_warning': 'Are you sure you want to show seeds? They are extremely sensitive.',
        'export_warning': 'Export seeds in plain text? Extreme risk!\nBe sure to protect the file.',
        'export_done': 'History exported. Protect the file with extreme care.',
        'no_wallets': 'No wallets with positive balance in history.',
        'results_cleared': 'Results area cleared.',
        'menu_theme': 'Theme',
        'theme_dark': 'Dark',
        'theme_light': 'Light',
        'menu_help': 'Help',
        'history': 'Wallets history',
        'scan_results': 'Scan results and error messages will appear here',
        'export_no_results': 'No results to export.',
        'login_exit': 'Exit',
        'change_lang': 'Language',
        'spanish': 'Spanish',
        'english': 'English',
    }
}

CURRENT_LANG = ['es']

def tr(key, **kwargs):
    lang = CURRENT_LANG[0]
    txt = LANGUAGES[lang].get(key, key)
    if kwargs:
        return txt.format(**kwargs)
    return txt

LICENSE_FILE = os.path.join(os.path.expanduser("~"), ".checker_crypto_license.json")
MONERO_PAYMENT_ADDRESS = "42Ec5nSjmTAS54VnwcWwKCcwvu81ofUxg5DsnWKppgUHEf5AXCPMkZFirAnJoufnF4i71LCkQzePLDRWjj9W6JsxC2y1LBF"
USAGE_LIMIT_FREE = 5

HISTORIAL_FILE = os.path.join(os.path.expanduser("~"), ".checker_crypto_historial")

# --- Funciones de cifrado para historial ---
def get_historial_key(user, pwd):
    # Deriva una clave Fernet simple del hash de usuario+pwd
    key = hashlib.sha256((user+pwd).encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key[:32]))

def save_historial(user, pwd, historial):
    f = get_historial_key(user, pwd)
    data = json.dumps(historial).encode()
    with open(HISTORIAL_FILE, 'wb') as file:
        file.write(f.encrypt(data))

def load_historial(user, pwd):
    if not os.path.exists(HISTORIAL_FILE):
        return []
    try:
        f = get_historial_key(user, pwd)
        with open(HISTORIAL_FILE, 'rb') as file:
            data = f.decrypt(file.read())
        return json.loads(data.decode())
    except Exception:
        return []

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr('login_title'))
        self.setMinimumWidth(350)
        layout = QFormLayout(self)
        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText(tr('user'))
        self.pwd_edit = QLineEdit()
        self.pwd_edit.setPlaceholderText(tr('password'))
        self.pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow(tr('user')+':', self.user_edit)
        layout.addRow(tr('password')+':', self.pwd_edit)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def get_credentials(self):
        return self.user_edit.text(), self.pwd_edit.text()

def hash_user_pwd(user, pwd):
    return hashlib.sha256((user+pwd).encode()).hexdigest()

def load_license():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, 'r') as f:
            return json.load(f)
    return None

def save_license(data):
    with open(LICENSE_FILE, 'w') as f:
        json.dump(data, f)

print("[DEBUG] main.py se está ejecutando antes de main()")
def main():
    print("[DEBUG] main() iniciado")
    try:
        print('[DEBUG] Cargando variables de entorno...')
        load_dotenv()  # Cargar variables de entorno
        print('[DEBUG] Variables de entorno cargadas')
        app = QApplication(sys.argv)
        print('[DEBUG] QApplication creada')
        window = MainWindow()
        print('[DEBUG] MainWindow creada')
        window.show()
        print('[DEBUG] Ventana mostrada')
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        user = None
        pwd = None
        while not logged_in:
            login = LoginDialog()
            login.setWindowTitle(tr('login_title'))
            if login.exec() == QDialog.DialogCode.Accepted:
                user, pwd = login.get_credentials()
                if not user or not pwd:
                    QMessageBox.warning(None, tr('login_title'), tr('login_required'))
                    continue
                user_hash = hash_user_pwd(user, pwd)
                if not license_data:
                    # Registro nuevo
                    license_data = {"user": user, "user_hash": user_hash, "licensed": False, "usage": 0}
                    save_license(license_data)
                    QMessageBox.information(None, tr('login_title'), tr('register_success'))
                    logged_in = True
                elif license_data["user"] == user and license_data["user_hash"] == user_hash:
                    logged_in = True
                else:
                    QMessageBox.critical(None, tr('login_title'), tr('login_failed'))
            else:
                sys.exit(0)

        # --- Ventana principal ---
        window = MainWindow()
        window.license_data = license_data
        window.check_license = lambda: load_license()
        window.prompt_payment = lambda: show_payment_dialog()
        window.increment_usage = lambda: increment_usage(window)
        window.logout = lambda: logout(app)
        window.show_account_info = lambda: show_account_info(window)
        window.account_info_dialog = None
        window.update_license_status()
        window.get_user_pwd = lambda: (user, pwd)
        window.show_historial = lambda: show_historial(window, user, pwd)
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error al iniciar la aplicación: {str(e)}")
        sys.exit(1)

        # --- Ventana principal ---
        window = MainWindow()
        window.license_data = license_data
        window.check_license = lambda: load_license()
        window.prompt_payment = lambda: show_payment_dialog()
        window.increment_usage = lambda: increment_usage(window)
        window.logout = lambda: logout(app)
        window.show_account_info = lambda: show_account_info(window)
        window.account_info_dialog = None
        window.update_license_status()
        window.get_user_pwd = lambda: (user, pwd)
        window.show_historial = lambda: show_historial(window, user, pwd)
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error al iniciar la aplicación: {str(e)}")
        sys.exit(1)

def show_account_info(window):
    # Obtiene datos de usuario/licencia y los muestra en un diálogo
    data = getattr(window, 'license_data', None)
    if not data:
        QMessageBox.information(window, "Información de cuenta", "No hay información de usuario disponible.")
        return
    user = data.get('user', 'N/A')
    licensed = data.get('licensed', False)
    usage = data.get('usage', 0)
    license_status = 'PRO' if licensed else 'Gratuita'
    msg = QMessageBox(window)
    msg.setWindowTitle("Información de cuenta")
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setText(f"<b>Usuario:</b> {user}<br>"
                f"<b>Licencia:</b> {license_status}<br>"
                f"<b>Escaneos usados:</b> {usage}")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()

def show_payment_dialog():
    msg = QMessageBox()
    msg.setWindowTitle("Adquirir Licencia PRO")
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setText("""
Para desbloquear Checker Crypto PRO:

1. Envía el pago a la siguiente dirección Monero:

<pre style='font-size:10px;'>%s</pre>

2. Adjunta el comprobante a tu usuario o contacta soporte.

Solo XMR. El proceso puede demorar unos minutos tras la verificación.
""" % MONERO_PAYMENT_ADDRESS)
    msg.setDetailedText(MONERO_PAYMENT_ADDRESS)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()

def increment_usage(window):
    data = load_license()
    if data:
        data["usage"] = data.get("usage",0)+1
        save_license(data)
        window.license_data = data
        return data["usage"]
    return 0

def show_historial(window, user, pwd):
    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
    import csv
    historial = load_historial(user, pwd)
    dialog = QDialog(window)
    dialog.setWindowTitle(tr('history'))
    layout = QVBoxLayout(dialog)
    if not historial:
        layout.addWidget(QLabel(tr('no_wallets')))
    else:
        table = QTableWidget(len(historial), 4)
        table.setHorizontalHeaderLabels([tr('user'), "Balance", "Seed", "Fecha/Hora"])
        # Por defecto, seeds ocultas
        seeds_visible = [False]
        def update_table():
            for i, entry in enumerate(historial):
                table.setItem(i, 0, QTableWidgetItem(entry["address"]))
                table.setItem(i, 1, QTableWidgetItem(str(entry["balance"])))
                table.setItem(i, 2, QTableWidgetItem(entry["seed"] if seeds_visible[0] else "••••••••••••••••••••••••"))
                table.setItem(i, 3, QTableWidgetItem(entry["datetime"]))
        update_table()
        layout.addWidget(table)
        toggle_btn = QPushButton(tr('show_hide_seeds'))
        def toggle_seeds():
            if not seeds_visible[0]:
                reply = QMessageBox.warning(dialog, tr('privacy_warning'), tr('privacy_warning'), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply != QMessageBox.StandardButton.Yes:
                    return
            seeds_visible[0] = not seeds_visible[0]
            update_table()
        toggle_btn.clicked.connect(toggle_seeds)
        layout.addWidget(toggle_btn)
        export_btn = QPushButton(tr('export_history'))
        def export_hist():
            reply = QMessageBox.warning(dialog, tr('export_warning'), tr('export_warning'), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return
            file_path, _ = QFileDialog.getSaveFileName(window, tr('export_history'), "historial.csv", "CSV Files (*.csv)")
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([tr('user'), "Balance", "Seed", "Fecha/Hora"])
                    for entry in historial:
                        writer.writerow([entry["address"], entry["balance"], entry["seed"], entry["datetime"]])
                QMessageBox.information(window, tr('export_done'), tr('export_done'))
        export_btn.clicked.connect(export_hist)
        layout.addWidget(export_btn)
    dialog.setLayout(layout)
    dialog.exec()

if __name__ == "__main__":
    main()