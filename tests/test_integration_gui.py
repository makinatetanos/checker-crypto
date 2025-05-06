import pytest
from PyQt6.QtCore import Qt
from verificador_monero.main import MainWindow

@pytest.fixture
def main_window(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    return window

# 1. Flujo completo: escaneo y visualización de resultados
def test_scan_button_triggers_scan_and_results(main_window, qtbot):
    button = main_window.start_button
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    qtbot.wait(1000)  # Espera a que el escaneo simulado avance
    assert button.text() in ["Detener Escaneo", "Iniciar Escaneo"]
    # Verifica que el área de resultados se actualiza
    assert "Wallet" in main_window.results_area.toPlainText() or "Error" in main_window.results_area.toPlainText()

# 2. Simular error de red y verificar feedback
@pytest.mark.usefixtures("main_window")
def test_scan_wallet_network_failure(qtbot, main_window, monkeypatch):
    def fake_refresh(*args, **kwargs):
        raise Exception("Network error simulated")
    from verificador_monero.wallet.monero_wallet import MoneroWallet
    monkeypatch.setattr(MoneroWallet, "refresh", fake_refresh)
    button = main_window.start_button
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    qtbot.wait(500)
    assert "Network error simulated" in main_window.results_area.toPlainText()

# 3. Persistencia/cierre limpio (si aplica)
def test_main_window_close_event(main_window, qtbot):
    # Simula cierre de ventana y asegura que no hay errores
    main_window.close()
    assert not main_window.isVisible()
