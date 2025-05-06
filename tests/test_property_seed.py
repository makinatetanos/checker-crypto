import pytest
from hypothesis import given, strategies as st
from verificador_monero.wallet.monero_wallet import MoneroWallet, WalletError

@given(seed=st.text(min_size=0, max_size=50))
def test_seed_property_based(seed):
    # Permite None solo explícitamente
    if seed is None or not isinstance(seed, str) or not seed.strip() or len(seed) < 10 or not seed.replace(' ', '').isalnum():
        with pytest.raises(WalletError):
            MoneroWallet(address="44A...", seed=seed, test_mode=False)
    else:
        # No debe lanzar excepción para seeds válidos
        MoneroWallet(address="44A...", seed=seed, test_mode=False)
