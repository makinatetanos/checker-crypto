import pytest
from PyQt6.QtCore import QObject
from verificador_monero.gui.wallet_scanner import WalletScanner

class SignalCatcher(QObject):
    def __init__(self):
        super().__init__()
        self.progress_values = []
        self.error_msgs = []
        self.wallets_found = []

    def on_progress(self, value):
        self.progress_values.append(value)

    def on_error(self, msg):
        self.error_msgs.append(msg)

    def on_wallet_found(self, wallet):
        self.wallets_found.append(wallet)

# Test de señales Qt emitidas por WalletScanner
def test_wallet_scanner_signals(qtbot):
    scanner = WalletScanner(test_mode=True)
    catcher = SignalCatcher()
    scanner.progress_updated.connect(catcher.on_progress)
    scanner.error_occurred.connect(catcher.on_error)
    scanner.wallet_found.connect(catcher.on_wallet_found)
    scanner.start()
    qtbot.wait(1000)  # Espera señales
    # Debe haber al menos un progreso y una wallet encontrada
    assert len(catcher.progress_values) > 0
    assert len(catcher.wallets_found) > 0
    # No debe haber errores en modo test
    assert len(catcher.error_msgs) == 0

# Simular error y comprobar señal error_occurred
def test_wallet_scanner_error_signal(qtbot, monkeypatch):
    scanner = WalletScanner(test_mode=True)
    catcher = SignalCatcher()
    scanner.error_occurred.connect(catcher.on_error)
    def fake_run():
        scanner.error_occurred.emit("Error simulado")
    monkeypatch.setattr(scanner, "run", fake_run)
    scanner.start()
    qtbot.wait(100)
    assert "Error simulado" in catcher.error_msgs
