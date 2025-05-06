import pytest
import os
import time
import sys
from pathlib import Path
from cryptography.fernet import Fernet

# Agregar el directorio src al path de Python
sys.path.append(str(Path(__file__).parent.parent))

from src.monero_handler import MoneroHandler, MoneroHandlerError

@pytest.fixture
def monero_handler():
    return MoneroHandler(test_mode=True)

def test_generate_seed(monero_handler):
    seed = monero_handler.generate_seed()
    assert isinstance(seed, str)
    assert len(seed.split()) >= 12  # Las frases semilla de Monero tienen al menos 12 palabras

def test_create_wallet(monero_handler):
    wallet = monero_handler.create_wallet()
    assert wallet is not None
    assert hasattr(wallet, 'address')
    assert isinstance(wallet.address(), str)
    assert monero_handler.validate_address(wallet.address())

def test_encrypt_decrypt_seed(monero_handler):
    original_seed = monero_handler.generate_seed()
    encrypted = monero_handler.encrypt_seed(original_seed)
    decrypted = monero_handler.decrypt_seed(encrypted)
    assert decrypted == original_seed

def test_validate_address(monero_handler):
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
    # Dirección válida de prueba
    address = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    balance = monero_handler.check_wallet_balance(address)
    assert isinstance(balance, float)
    assert balance >= 0

def test_is_wallet_lost(monero_handler):
    # Dirección válida de prueba
    address = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    is_lost = monero_handler.is_wallet_lost(address)
    assert isinstance(is_lost, bool)

def test_error_handling(monero_handler):
    # Probar manejo de errores con datos inválidos
    with pytest.raises(MoneroHandlerError):
        monero_handler.check_wallet_balance("invalid_address")
    
    with pytest.raises(MoneroHandlerError):
        monero_handler.encrypt_seed(123)  # Tipo de dato inválido
    
    with pytest.raises(MoneroHandlerError):
        monero_handler.decrypt_seed("not_bytes")  # Tipo de dato inválido

def test_rate_limiting(monero_handler):
    # Probar que el rate limiting funciona
    start_time = time.time()
    
    # Hacer múltiples llamadas rápidas
    address = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    for _ in range(3):
        try:
            monero_handler.check_wallet_balance(address)
        except MoneroHandlerError:
            pass  # Ignorar errores de API
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Debería haber tomado al menos 2 segundos (1 segundo entre cada llamada)
    assert elapsed_time >= 2

def test_create_wallet_with_seed(monero_handler):
    # Probar crear wallet con una seed específica
    seed = monero_handler.generate_seed()
    wallet = monero_handler.create_wallet(seed=seed)
    assert wallet is not None
    assert hasattr(wallet, 'address')
    assert isinstance(wallet.address(), str)

def test_multiple_seed_generation(monero_handler):
    # Probar que las seeds generadas son diferentes
    seed1 = monero_handler.generate_seed()
    seed2 = monero_handler.generate_seed()
    assert seed1 != seed2

def test_encryption_consistency(monero_handler):
    # Probar que la encriptación y desencriptación son consistentes
    seed = monero_handler.generate_seed()
    encrypted = monero_handler.encrypt_seed(seed)
    decrypted = monero_handler.decrypt_seed(encrypted)
    assert decrypted == seed  # La desencriptación debe devolver la seed original

def test_invalid_encryption_key(monero_handler):
    # Probar manejo de clave de encriptación inválida
    with pytest.raises(MoneroHandlerError):  # Fernet lanza MoneroHandlerError con claves inválidas
        monero_handler.cipher_suite = Fernet(b'invalid_key')
        monero_handler.encrypt_seed("test_seed")

def test_wallet_creation_with_invalid_seed(monero_handler):
    # Probar crear wallet con seed inválida
    with pytest.raises(MoneroHandlerError):  # Seed inválida debería lanzar MoneroHandlerError
        monero_handler.create_wallet(seed="invalid_seed_format")

def test_balance_check_with_invalid_address_format(monero_handler):
    # Probar verificación de balance con formato de dirección inválido
    with pytest.raises(MoneroHandlerError):
        monero_handler.check_wallet_balance("invalid_format_address")

def test_wallet_lost_check_with_invalid_address(monero_handler):
    # Probar verificación de wallet perdida con dirección inválida
    with pytest.raises(MoneroHandlerError):
        monero_handler.is_wallet_lost("invalid_address")

def test_encryption_with_empty_seed(monero_handler):
    # Probar encriptación con seed vacía
    with pytest.raises(MoneroHandlerError):  # Seed vacía debería lanzar MoneroHandlerError
        monero_handler.encrypt_seed("")

def test_decryption_with_invalid_data(monero_handler):
    # Probar desencriptación con datos inválidos
    with pytest.raises(MoneroHandlerError):
        monero_handler.decrypt_seed(b'invalid_encrypted_data')

def test_validate_address_edge_cases(monero_handler):
    # Probar casos límite en validación de dirección
    assert monero_handler.validate_address("4" + "1" * 94) is True  # Dirección válida
    assert monero_handler.validate_address("3" + "1" * 94) is False  # Prefijo inválido
    assert monero_handler.validate_address("4" + "1" * 93) is False  # Longitud incorrecta

def test_rate_limiting_edge_cases(monero_handler):
    # Probar casos límite en rate limiting
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
    # Probar operaciones concurrentes en la wallet
    address = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    
    # Realizar múltiples operaciones
    balance = monero_handler.check_wallet_balance(address)
    is_lost = monero_handler.is_wallet_lost(address)
    is_valid = monero_handler.validate_address(address)
    
    assert isinstance(balance, float)
    assert isinstance(is_lost, bool)
    assert isinstance(is_valid, bool) 