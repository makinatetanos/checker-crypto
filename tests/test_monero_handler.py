import pytest
import os
import time
import sys
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

# Agregar el directorio src al path de Python
sys.path.append(str(Path(__file__).parent.parent))

from src.verificador_monero.monero_handler import (
    MoneroHandler, MoneroHandlerError,
    SimulatedWallet, Seed, JSONRPCWallet
)

@pytest.fixture
def monero_handler():
    """Fixture que proporciona una instancia de MoneroHandler en modo de prueba"""
    return MoneroHandler(test_mode=True)

@pytest.fixture
def monero_handler_no_env():
    """Fixture que proporciona una instancia de MoneroHandler sin variables de entorno"""
    # Guardar variables de entorno actuales
    old_env = {}
    for key in ['ENCRYPTION_KEY', 'MONERO_RPC_HOST', 'MONERO_RPC_PORT', 'MONERO_RPC_USER', 'MONERO_RPC_PASSWORD']:
        if key in os.environ:
            old_env[key] = os.environ[key]
            del os.environ[key]
    
    # Crear instancia sin variables de entorno
    handler = MoneroHandler(test_mode=True)
    
    # Restaurar variables de entorno
    for key, value in old_env.items():
        os.environ[key] = value
    
    return handler

@pytest.fixture
def monero_handler_with_invalid_key():
    """Fixture que proporciona una instancia de MoneroHandler con una clave de encriptación inválida"""
    os.environ['ENCRYPTION_KEY'] = 'invalid_key'
    handler = MoneroHandler(test_mode=True)
    return handler

def test_initialization(monero_handler):
    """Prueba la inicialización básica del MoneroHandler"""
    assert monero_handler.test_mode is True
    assert monero_handler.rate_limit_delay == 1
    assert monero_handler.last_request_time == 0

def test_initialization_no_env(monero_handler_no_env):
    """Prueba la inicialización sin variables de entorno"""
    assert monero_handler_no_env.test_mode is True
    assert monero_handler_no_env.encryption_key is not None

def test_rate_limiting(monero_handler):
    """Prueba que el rate limiting funciona correctamente"""
    start_time = time.time()
    
    # Hacer múltiples llamadas rápidas
    address = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    for _ in range(3):
        monero_handler.check_wallet_balance(address)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Debería haber tomado al menos 2 segundos (1 segundo entre cada llamada)
    assert elapsed_time >= 2

def test_generate_seed(monero_handler):
    """Prueba la generación de seeds"""
    seed = monero_handler.generate_seed()
    assert isinstance(seed, str)
    assert len(seed.split()) >= 12  # Las frases semilla de Monero tienen al menos 12 palabras

def test_create_wallet(monero_handler):
    """Prueba la creación de wallets"""
    # Crear wallet sin seed
    wallet = monero_handler.create_wallet()
    assert wallet is not None
    assert hasattr(wallet, 'address')
    assert isinstance(wallet.address(), str)
    assert monero_handler.validate_address(wallet.address())
    
    # Crear wallet con seed
    seed = monero_handler.generate_seed()
    wallet_with_seed = monero_handler.create_wallet(seed=seed)
    assert wallet_with_seed is not None
    assert hasattr(wallet_with_seed, 'address')
    assert isinstance(wallet_with_seed.address(), str)

def test_validate_address(monero_handler):
    """Prueba la validación de direcciones"""
    # Dirección válida de Monero (la de prueba)
    valid_address = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    assert monero_handler.validate_address(valid_address) is True

    # Dirección inválida
    invalid_address = "1" + "1" * 94
    assert monero_handler.validate_address(invalid_address) is False

    # Tipos de datos inválidos
    assert monero_handler.validate_address(None) is False
    assert monero_handler.validate_address(123) is False
    assert monero_handler.validate_address("") is False

def test_check_wallet_balance(monero_handler):
    """Prueba la verificación de balance de wallets"""
    # Dirección válida de prueba
    address = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    balance = monero_handler.check_wallet_balance(address)
    assert isinstance(balance, float)
    assert balance >= 0

def test_is_wallet_lost(monero_handler):
    """Prueba la verificación de wallets perdidas"""
    # Dirección válida de prueba
    address = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    is_lost = monero_handler.is_wallet_lost(address)
    assert isinstance(is_lost, bool)

def test_encrypt_decrypt_seed(monero_handler):
    """Prueba la encriptación y desencriptación de seeds"""
    original_seed = monero_handler.generate_seed()
    encrypted = monero_handler.encrypt_seed(original_seed)
    decrypted = monero_handler.decrypt_seed(encrypted)
    assert decrypted == original_seed

def test_error_handling(monero_handler):
    """Prueba el manejo de errores"""
    # Probar manejo de errores con datos inválidos
    with pytest.raises(MoneroHandlerError):
        monero_handler.check_wallet_balance("invalid_address")
    
    with pytest.raises(MoneroHandlerError):
        monero_handler.encrypt_seed(123)  # Tipo de dato inválido
    
    with pytest.raises(MoneroHandlerError):
        monero_handler.decrypt_seed("not_bytes")  # Tipo de dato inválido

def test_wallet_creation_with_invalid_seed(monero_handler):
    """Prueba la creación de wallet con seed inválida"""
    with pytest.raises(MoneroHandlerError):
        monero_handler.create_wallet(seed="invalid_seed_format")

def test_balance_check_with_invalid_address_format(monero_handler):
    """Prueba la verificación de balance con formato de dirección inválido"""
    with pytest.raises(MoneroHandlerError):
        monero_handler.check_wallet_balance("invalid_format_address")

def test_wallet_lost_check_with_invalid_address(monero_handler):
    """Prueba la verificación de wallet perdida con dirección inválida"""
    with pytest.raises(MoneroHandlerError):
        monero_handler.is_wallet_lost("invalid_address")

def test_encryption_with_empty_seed(monero_handler):
    """Prueba la encriptación con seed vacía"""
    with pytest.raises(MoneroHandlerError):
        monero_handler.encrypt_seed("")

def test_decryption_with_invalid_data(monero_handler):
    """Prueba la desencriptación con datos inválidos"""
    with pytest.raises(MoneroHandlerError):
        monero_handler.decrypt_seed(b'invalid_encrypted_data')

def test_validate_address_edge_cases(monero_handler):
    """Prueba casos límite en validación de dirección"""
    assert monero_handler.validate_address("4" + "1" * 94) is True  # Dirección válida
    assert monero_handler.validate_address("3" + "1" * 94) is False  # Prefijo inválido
    assert monero_handler.validate_address("4" + "1" * 93) is False  # Longitud incorrecta

def test_rate_limiting_edge_cases(monero_handler):
    """Prueba casos límite en rate limiting"""
    address = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    
    # Primera llamada
    monero_handler.check_wallet_balance(address)
    first_time = monero_handler.last_request_time
    
    # Segunda llamada inmediata
    monero_handler.check_wallet_balance(address)
    second_time = monero_handler.last_request_time
    
    # Debería haber una diferencia de al menos 1 segundo
    assert second_time - first_time >= 1

def test_concurrent_wallet_operations(monero_handler):
    """Prueba operaciones concurrentes en la wallet"""
    address = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    
    # Realizar múltiples operaciones
    balance = monero_handler.check_wallet_balance(address)
    is_lost = monero_handler.is_wallet_lost(address)
    is_valid = monero_handler.validate_address(address)
    
    assert isinstance(balance, float)
    assert isinstance(is_lost, bool)
    assert isinstance(is_valid, bool)

def test_monero_import_error(monkeypatch):
    """Test de error al importar monero"""
    def mock_import(*args, **kwargs):
        raise ImportError("Error simulado")
    
    monkeypatch.setattr("importlib.import_module", mock_import)
    
    # Crear una nueva instancia debería usar las clases simuladas
    handler = MoneroHandler(test_mode=True)
    assert handler.test_mode is True

def test_simulated_wallet_methods():
    """Test de los métodos de la wallet simulada"""
    wallet = SimulatedWallet()
    
    # Probar dirección
    address = wallet.address()
    assert isinstance(address, str)
    assert len(address) > 0
    
    # Probar refresh
    wallet.refresh()  # No debería hacer nada

def test_simulated_seed_methods():
    """Test de los métodos de la seed simulada"""
    # Probar seed sin frase
    seed = Seed()
    assert isinstance(seed.phrase, str)
    assert len(seed.phrase.split()) == 25
    
    # Probar seed con frase
    test_phrase = "test " * 25
    seed = Seed(test_phrase)
    assert seed.phrase == test_phrase

def test_simulated_jsonrpc_wallet():
    """Test de la wallet RPC simulada"""
    wallet = JSONRPCWallet("localhost", 18081, "user", "pass")
    assert wallet.host == "localhost"
    assert wallet.port == 18081

def test_encryption_edge_cases(monero_handler):
    """Test de casos límite de encriptación/desencriptación"""
    # Probar encriptación con seed vacía
    with pytest.raises(MoneroHandlerError):
        monero_handler.encrypt_seed("")
    
    # Probar desencriptación con datos inválidos
    with pytest.raises(MoneroHandlerError):
        monero_handler.decrypt_seed("datos_invalidos")
    
    # Probar desencriptación con datos no base64
    with pytest.raises(MoneroHandlerError):
        monero_handler.decrypt_seed("!@#$%^&*()")

def test_balance_check_edge_cases(monero_handler):
    """Test de casos límite de verificación de balance"""
    # Probar dirección inválida
    with pytest.raises(MoneroHandlerError):
        monero_handler.check_wallet_balance("dirección_inválida")
    
    # Probar dirección vacía
    with pytest.raises(MoneroHandlerError):
        monero_handler.check_wallet_balance("")

def test_wallet_lost_edge_cases(monero_handler):
    """Test de casos límite de verificación de wallet perdida"""
    # Probar dirección inválida
    with pytest.raises(MoneroHandlerError):
        monero_handler.is_wallet_lost("dirección_inválida")
    
    # Probar dirección vacía
    with pytest.raises(MoneroHandlerError):
        monero_handler.is_wallet_lost("")

def test_address_validation_edge_cases(monero_handler):
    """Test de casos límite de validación de direcciones"""
    # Probar dirección muy corta
    assert not monero_handler.validate_address("123")
    
    # Probar dirección muy larga
    assert not monero_handler.validate_address("A" * 200)
    
    # Probar dirección con caracteres inválidos
    assert not monero_handler.validate_address("!@#$%^&*()") 