import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from ..app import MoneroApp, ScannerThread
from ..config import MoneroConfig
from ..wallet import MoneroWallet

@pytest.fixture
def app(qtbot):
    config = MoneroConfig()
    window = MoneroApp(config)
    qtbot.addWidget(window)
    return window

def test_app_initialization(app):
    assert app.config is not None
    assert app.wallet_manager is not None
    assert app.scanner is None
    assert app.dark_mode is True

def test_app_ui_elements(app):
    assert app.rpc_host_input is not None
    assert app.rpc_port_input is not None
    assert app.test_mode_check is not None
    assert app.max_threads_input is not None
    assert app.scan_interval_input is not None
    assert app.max_attempts_input is not None
    assert app.start_button is not None
    assert app.dark_mode_button is not None
    assert app.progress_bar is not None
    assert app.results_text is not None

def test_app_config_inputs(app):
    app.rpc_host_input.setText("test_host")
    app.rpc_port_input.setText("12345")
    app.test_mode_check.setChecked(False)
    app.max_threads_input.setValue(8)
    app.scan_interval_input.setValue(2000)
    app.max_attempts_input.setValue(5000)

    assert app.config.rpc_host == "test_host"
    assert app.config.rpc_port == "12345"
    assert app.config.test_mode is False
    assert app.config.max_threads == 8
    assert app.config.scan_interval_ms == 2000
    assert app.config.max_attempts == 5000

def test_app_theme_toggle(app):
    initial_theme = app.dark_mode
    app.toggle_theme()
    assert app.dark_mode != initial_theme

def test_app_scanning_toggle(app, qtbot):
    # Iniciar escaneo
    qtbot.mouseClick(app.start_button, Qt.MouseButton.LeftButton)
    assert app.scanner is not None
    assert app.scanner.is_running

    # Detener escaneo
    qtbot.mouseClick(app.start_button, Qt.MouseButton.LeftButton)
    assert not app.scanner.is_running

def test_app_progress_update(app, qtbot):
    app.start_scanning()
    app.update_progress(50.0)
    assert app.progress_bar.value() == 50

def test_app_wallet_result(app, qtbot):
    wallet = MoneroWallet(
        address="4" + "1" * 94,
        balance=1.0,
        is_lost=True
    )
    app.add_wallet_result(wallet)
    assert "Wallet encontrada" in app.results_text.toPlainText()
    assert wallet.address in app.results_text.toPlainText()
    assert format_balance(wallet.balance) in app.results_text.toPlainText()

def test_app_error_handling(app, qtbot):
    app.show_error("Test error")
    assert "Error: Test error" in app.results_text.toPlainText()

def test_app_scanning_finished(app, qtbot):
    app.scanning_finished()
    assert app.start_button.text() == "Iniciar Escaneo"
    assert app.progress_bar.value() == 100

def test_app_stats_update(app, qtbot):
    wallet = MoneroWallet(
        address="4" + "1" * 94,
        balance=1.0,
        is_lost=True
    )
    app.add_wallet_result(wallet)
    app.update_stats()
    assert app.wallets_found_label.text() == "1"
    assert app.total_balance_label.text() == format_balance(1.0)

def test_scanner_thread(app):
    scanner = ScannerThread(app.config, app.wallet_manager)
    assert scanner.config == app.config
    assert scanner.wallet_manager == app.wallet_manager
    assert not scanner.is_running
    assert scanner.attempts == 0

def test_scanner_thread_stop(app):
    scanner = ScannerThread(app.config, app.wallet_manager)
    scanner.is_running = True
    scanner.stop()
    assert not scanner.is_running 