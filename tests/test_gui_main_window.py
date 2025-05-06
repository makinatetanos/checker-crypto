import pytest
from PyQt6.QtWidgets import QApplication
from verificador_monero.gui.main_window import MainWindow

@pytest.fixture
def main_window(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    return window

def test_main_window_init(main_window):
    assert main_window.windowTitle() == "Verificador de Monero"
    assert main_window.progress_bar.value() == 0

def test_start_scanning_sets_button_text(main_window, qtbot):
    main_window.start_scanning()
    assert main_window.start_button.text() == "Detener Escaneo"
    main_window.start_scanning()
    assert main_window.start_button.text() == "Iniciar Escaneo"

def test_show_error(main_window, qtbot):
    main_window.show_error("Mensaje de error de prueba")
    assert "Error: Mensaje de error de prueba" in main_window.results_area.toPlainText()
