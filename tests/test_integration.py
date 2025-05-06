import pytest
from src.verificador_monero.monero_handler import MoneroHandler

def test_full_wallet_flow():
    handler = MoneroHandler(test_mode=True)

    # 1. Generar seed y crear wallet
    seed = handler.generate_seed()
    wallet = handler.create_wallet(seed=seed)
    address = wallet.address()
    assert isinstance(seed, str)
    assert isinstance(address, str)
    assert len(address) > 0

    # 2. Cifrar y descifrar la seed
    encrypted = handler.encrypt_seed(seed)
    decrypted = handler.decrypt_seed(encrypted)
    assert decrypted == seed

    # 3. Verificar balance (modo test)
    balance = handler.check_wallet_balance(address)
    assert isinstance(balance, float)

    # 4. Verificar si la wallet está perdida (modo test)
    lost = handler.is_wallet_lost(address)
    assert isinstance(lost, bool)

    # 5. Validar dirección
    assert handler.validate_address(address)
