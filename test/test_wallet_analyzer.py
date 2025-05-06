import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Agregar el directorio src al path de Python
sys.path.append(str(Path(__file__).parent.parent))

from src.wallet_analyzer import WalletAnalyzer
from src.monero_handler import MoneroHandler

@pytest.fixture
def mock_monero_handler():
    handler = Mock(spec=MoneroHandler)
    # Configurar comportamiento por defecto
    handler.validate_address.return_value = True
    handler.check_wallet_balance.return_value = 1.0
    handler.is_wallet_lost.return_value = False
    return handler

@pytest.fixture
def wallet_analyzer(mock_monero_handler):
    return WalletAnalyzer(monero_handler=mock_monero_handler)

def test_analizar_wallet_valida(wallet_analyzer, mock_monero_handler):
    direccion = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    resultado = wallet_analyzer.analizar_wallet(direccion)
    
    assert resultado["direccion"] == direccion
    assert resultado["balance"] == 1.0
    assert resultado["esta_perdida"] is False
    assert resultado["estado"] == "activa"
    assert resultado["error"] is None

def test_analizar_wallet_invalida(wallet_analyzer, mock_monero_handler):
    mock_monero_handler.validate_address.return_value = False
    direccion = "direccion_invalida"
    
    resultado = wallet_analyzer.analizar_wallet(direccion)
    
    assert resultado["direccion"] == direccion
    assert resultado["estado"] == "error"
    assert "inválida" in str(resultado["error"]).lower()

def test_analizar_wallet_perdida(wallet_analyzer, mock_monero_handler):
    mock_monero_handler.is_wallet_lost.return_value = True
    direccion = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    
    resultado = wallet_analyzer.analizar_wallet(direccion)
    
    assert resultado["direccion"] == direccion
    assert resultado["esta_perdida"] is True
    assert resultado["estado"] == "perdida"

def test_analizar_multiple_wallets(wallet_analyzer):
    direcciones = [
        "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A",
        "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3B"
    ]
    
    resultados = wallet_analyzer.analizar_multiple_wallets(direcciones)
    
    assert len(resultados) == 2
    assert all(r["estado"] == "activa" for r in resultados)

def test_obtener_estadisticas(wallet_analyzer, mock_monero_handler):
    # Configurar diferentes estados para las wallets
    mock_monero_handler.is_wallet_lost.side_effect = [True, False, False]
    
    direcciones = [
        "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A",
        "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3B",
        "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3C"
    ]
    
    for dir in direcciones:
        wallet_analyzer.analizar_wallet(dir)
    
    stats = wallet_analyzer.obtener_estadisticas()
    
    assert stats["total_wallets"] == 3
    assert stats["wallets_perdidas"] == 1
    assert stats["wallets_activas"] == 2
    assert stats["wallets_error"] == 0
    assert stats["balance_total"] == 3.0  # 1.0 por cada wallet

def test_limpiar_resultados(wallet_analyzer):
    direccion = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    wallet_analyzer.analizar_wallet(direccion)
    assert len(wallet_analyzer.resultados) == 1
    
    wallet_analyzer.limpiar_resultados()
    assert len(wallet_analyzer.resultados) == 0

def test_error_en_balance(wallet_analyzer, mock_monero_handler):
    mock_monero_handler.check_wallet_balance.side_effect = Exception("Error al obtener balance")
    direccion = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    
    resultado = wallet_analyzer.analizar_wallet(direccion)
    
    assert resultado["estado"] == "error"
    assert "Error al obtener balance" in str(resultado["error"])
