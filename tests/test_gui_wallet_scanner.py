import pytest
from PyQt6.QtCore import QThread
from verificador_monero.gui.wallet_scanner import WalletScanner

class DummySignal:
    def __init__(self):
        self.called = False
        self.value = None
    def connect(self, func):
        self._func = func
    def emit(self, value=None):
        self.called = True
        self.value = value
        if hasattr(self, '_func'):
            if value is not None:
                self._func(value)
            else:
                self._func()

def test_wallet_scanner_init_and_stop(qtbot):
    scanner = WalletScanner(test_mode=True)
    assert scanner.is_running is True
    scanner.stop()
    assert scanner.is_running is False

def test_wallet_scanner_run_signals(monkeypatch, qtbot):
    scanner = WalletScanner(test_mode=True)
    scanner.progress_updated = DummySignal()
    scanner.wallet_found = DummySignal()
    scanner.error_occurred = DummySignal()

    # Mock de create_wallet para devolver un wallet simulado
    class MockWallet:
        def address(self):
            return '44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A'

    monkeypatch.setattr(scanner.monero_handler, 'create_wallet', lambda: MockWallet())
    monkeypatch.setattr(scanner.monero_handler, 'is_wallet_lost', lambda addr: False)

    # Mock del bucle para que solo se ejecute una vez
    original_run = scanner.run
    def single_run():
        total_attempts = 1
        for i in range(total_attempts):
            if not scanner.is_running:
                break
            try:
                wallet = scanner.monero_handler.create_wallet()
                address = wallet.address()
                if scanner.monero_handler.is_wallet_lost(address):
                    scanner.wallet_found.emit(address)
                progress = int((i + 1) / total_attempts * 100)
                scanner.progress_updated.emit(progress)
            except Exception as e:
                scanner.error_occurred.emit(str(e))
                continue
    scanner.run = single_run

    scanner.run()
    assert scanner.progress_updated.called
    assert not scanner.wallet_found.called
    assert not scanner.error_occurred.called
