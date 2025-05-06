import pytest
from verificador_monero.wallet.monero_wallet import MoneroWallet, WalletError
from datetime import datetime, timedelta

def test_monero_wallet_init():
    wallet = MoneroWallet(address="44A...", seed="seed", test_mode=True)
    assert wallet.address == "44A..."
    assert wallet.seed == "seed"
    assert wallet.test_mode is True

def test_monero_wallet_refresh_and_balance():
    wallet = MoneroWallet(test_mode=True)
    wallet.refresh()
    assert wallet._balance == 1.0
    assert isinstance(wallet._last_transaction, datetime)
    balance = wallet.check_balance()
    assert balance == 1.0

    # Forzamos excepción en modo real
    wallet_real = MoneroWallet(test_mode=False)
    with pytest.raises(WalletError):
        wallet_real.refresh()

    with pytest.raises(WalletError):
        wallet_real.check_balance()

def test_monero_wallet_is_lost():
    wallet = MoneroWallet(test_mode=True)
    wallet.refresh()
    # Simula wallet "perdida" si la última transacción fue hace más de 365 días
    wallet._last_transaction = datetime.now() - timedelta(days=366)
    assert wallet.is_lost() is True
    wallet._last_transaction = datetime.now()
    assert wallet.is_lost() is False
