import pytest
from PyQt6.QtWidgets import QApplication
from verificador_monero.main import MainWindow, WalletScanner

@pytest.fixture(scope="session")
def app():
    app = QApplication([])
    yield app

@pytest.fixture
def main_window(app):
    window = MainWindow()
    return window

def test_main_window_title(main_window):
    assert main_window.windowTitle() == "Verificador de Monero"
    assert main_window.minimumWidth() == 800

def test_main_window_elements(main_window):
    # Verifica que los elementos principales existen
    assert hasattr(main_window, 'start_button')
    assert hasattr(main_window, 'progress_bar')
    assert hasattr(main_window, 'results_area')

# Test básico del scanner (solo instanciación y parada)
def test_wallet_scanner_basic():
    scanner = WalletScanner(test_mode=True)
    assert scanner.is_running
    scanner.stop()
    assert not scanner.is_running
