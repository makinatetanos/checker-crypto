#!/usr/bin/env python
import pytest
import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """Verifica que todas las dependencias necesarias estén instaladas"""
    try:
        import pytest
        import pytest_cov
        import pytest_qt
        import pytest_xvfb
        return True
    except ImportError as e:
        print(f"Error: Falta instalar dependencias de desarrollo: {e}")
        print("Ejecuta: pip install -e .[dev]")
        return False

def main():
    """Ejecuta los tests del proyecto"""
    if not check_dependencies():
        return 1

    # Configurar el directorio de trabajo
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)

    # Verificar que estamos en el directorio correcto
    if not (project_root / "tests").exists():
        print("Error: No se encontró el directorio de tests")
        return 1

    try:
        # Ejecutar los tests
        result = pytest.main([
            "tests",
            "-v",
            "--cov=verificador_monero",
            "--cov-report=term-missing",
            "--cov-report=html",
            "--no-cov-on-fail"
        ])
        
        # Generar reporte de cobertura en HTML
        if result == 0:
            print("\nReporte de cobertura generado en: htmlcov/index.html")
        
        return result
    except Exception as e:
        print(f"Error al ejecutar los tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 