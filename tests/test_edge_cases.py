import pytest
from verificador_monero.utils import validate_monero_address
from verificador_monero.wallet.monero_wallet import MoneroWallet, WalletError

# 1. Edge cases para direcciones Monero
@pytest.mark.parametrize("address", [
    "", "123", "ZZZZ...", "44A...incorrectlength", None
])
def test_invalid_monero_addresses(address):
    assert not validate_monero_address(address)

# 2. Edge cases para seeds
@pytest.mark.parametrize("seed", [
    "", "shortseed", "seedwithspecialchars!@#"
])
def test_invalid_seed_init(seed):
    with pytest.raises(Exception):
        MoneroWallet(address="44A...", seed=seed, test_mode=True)

# 3. Balance negativo o anómalo (simulación)
def test_negative_balance(monkeypatch):
    wallet = MoneroWallet(seed=None, test_mode=True)
    monkeypatch.setattr(wallet, "_balance", -10.0)
    assert wallet._balance < 0

# 4. Property-based: fuzzing de direcciones
from hypothesis import given, strategies as st

@given(st.text(min_size=0, max_size=100))
def test_address_validation_fuzz(address):
    # No debe lanzar excepción nunca
    validate_monero_address(address)
