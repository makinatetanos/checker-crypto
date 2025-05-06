import pytest
import os
import sys
from pathlib import Path

# Agregar el directorio src al path de Python
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path.absolute()))

# Configuración de pytest
def pytest_configure(config):
    """Configuración global de pytest"""
    config.addinivalue_line(
        "markers",
        "gui: marcar tests que requieren interfaz gráfica"
    )
    config.addinivalue_line(
        "markers",
        "slow: marcar tests que toman más tiempo"
    )
    config.addinivalue_line(
        "markers",
        "integration: marcar tests de integración"
    )

@pytest.fixture(scope="session")
def test_env():
    """Fixture para configurar el entorno de pruebas"""
    # Crear directorio temporal para archivos de prueba
    test_dir = Path(__file__).parent / "test_files"
    test_dir.mkdir(exist_ok=True)
    
    # Configurar variables de entorno para pruebas
    os.environ["TEST_MODE"] = "true"
    os.environ["MONERO_RPC_HOST"] = "localhost"
    os.environ["MONERO_RPC_PORT"] = "18081"
    
    yield test_dir
    
    # Limpieza después de las pruebas
    if test_dir.exists():
        for file in test_dir.glob("*"):
            file.unlink()
        test_dir.rmdir() 