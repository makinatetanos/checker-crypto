import pytest
from verificador_monero import utils

def test_encrypt_decrypt_data():
    key = "clave_secreta_para_pruebas"
    data = "mensaje secreto"
    encrypted = utils.encrypt_data(data, key)
    assert isinstance(encrypted, bytes)
    decrypted = utils.decrypt_data(encrypted, key)
    assert decrypted == data

    # Prueba error con clave incorrecta
    with pytest.raises(ValueError):
        utils.decrypt_data(encrypted, "clave_incorrecta")

    # Prueba error con datos vacíos
    with pytest.raises(ValueError):
        utils.encrypt_data("", key)
    with pytest.raises(ValueError):
        utils.encrypt_data(data, "")
    with pytest.raises(ValueError):
        utils.decrypt_data(b"", key)
    with pytest.raises(ValueError):
        utils.decrypt_data(encrypted, "")

def test_validate_monero_address():
    # Dirección válida
    valid = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    assert utils.validate_monero_address(valid)
    # Dirección inválida
    assert not utils.validate_monero_address("1234")
    assert not utils.validate_monero_address("")
    assert not utils.validate_monero_address(None)
