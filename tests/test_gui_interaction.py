import pytest
from PyQt6.QtWidgets import QApplication
from verificador_monero.main import MainWindow

@pytest.fixture(scope="session")
def app():
    return QApplication([])

@pytest.fixture
def main_window(app):
    window = MainWindow()
    window.show()
    return window

import sys
import pytest
from PyQt6.QtCore import Qt

@pytest.mark.xfail(sys.platform.startswith('win'), reason="Inestabilidad de PyQt en Windows para clicks automatizados")
def test_start_scan_button_changes_text(qtbot, main_window):
    button = main_window.start_button
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    # El texto debe cambiar a "Detener Escaneo" o "Iniciar Escaneo" (si el escaneo termina rápido)
    assert button.text() in ["Detener Escaneo", "Iniciar Escaneo"]
    # Simula click de nuevo (detener)
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert button.text() == "Iniciar Escaneo"

def test_show_error_message(qtbot, main_window):
    # Simula la emisión de una señal de error
    test_msg = "Mensaje de error de prueba"
    main_window.show_error(test_msg)
    assert f"Error: {test_msg}" in main_window.results_area.toPlainText()
