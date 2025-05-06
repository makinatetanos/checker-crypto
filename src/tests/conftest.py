import pytest
from PyQt6.QtWidgets import QApplication
 
@pytest.fixture(scope="session")
def qapp():
    app = QApplication([])
    yield app
    app.quit() 