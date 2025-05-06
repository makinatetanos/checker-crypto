import pytest
import asyncio
from datetime import datetime
from ..wallet import MoneroWallet, WalletManager
from ..utils import generate_seed

@pytest.fixture
def wallet_manager():
    return WalletManager("test_data")

@pytest.fixture
def test_wallet():
    return MoneroWallet(
        address="4" + "1" * 94,
        balance=1.0,
        is_lost=True,
        last_checked=datetime.now()
    )

@pytest.mark.asyncio
async def test_add_wallet(wallet_manager, test_wallet):
    assert await wallet_manager.add_wallet(test_wallet)
    assert not await wallet_manager.add_wallet(test_wallet)  # No duplicados

@pytest.mark.asyncio
async def test_get_wallet(wallet_manager, test_wallet):
    await wallet_manager.add_wallet(test_wallet)
    retrieved = await wallet_manager.get_wallet(test_wallet.address)
    assert retrieved is not None
    assert retrieved.address == test_wallet.address
    assert retrieved.balance == test_wallet.balance

@pytest.mark.asyncio
async def test_update_wallet(wallet_manager, test_wallet):
    await wallet_manager.add_wallet(test_wallet)
    new_balance = 2.0
    assert await wallet_manager.update_wallet(test_wallet.address, balance=new_balance)
    updated = await wallet_manager.get_wallet(test_wallet.address)
    assert updated.balance == new_balance

@pytest.mark.asyncio
async def test_remove_wallet(wallet_manager, test_wallet):
    await wallet_manager.add_wallet(test_wallet)
    assert await wallet_manager.remove_wallet(test_wallet.address)
    assert await wallet_manager.get_wallet(test_wallet.address) is None

@pytest.mark.asyncio
async def test_get_all_wallets(wallet_manager):
    wallets = [
        MoneroWallet(address="4" + str(i) * 94, balance=float(i))
        for i in range(3)
    ]
    for wallet in wallets:
        await wallet_manager.add_wallet(wallet)
    all_wallets = await wallet_manager.get_all_wallets()
    assert len(all_wallets) == 3

@pytest.mark.asyncio
async def test_get_lost_wallets(wallet_manager):
    wallets = [
        MoneroWallet(address="4" + str(i) * 94, balance=float(i), is_lost=i % 2 == 0)
        for i in range(4)
    ]
    for wallet in wallets:
        await wallet_manager.add_wallet(wallet)
    lost_wallets = await wallet_manager.get_lost_wallets()
    assert len(lost_wallets) == 2

def test_wallet_validation():
    with pytest.raises(ValueError):
        MoneroWallet(address="5" + "1" * 94, balance=1.0)
    with pytest.raises(ValueError):
        MoneroWallet(address="4" + "1" * 93, balance=1.0)
    with pytest.raises(ValueError):
        MoneroWallet(address="4" + "1" * 94, balance=-1.0)

@pytest.mark.asyncio
async def test_check_balance(wallet_manager):
    address = "4" + "1" * 94
    balance = await wallet_manager.check_balance(address, "http://localhost:18081/json_rpc")
    assert balance is not None
    assert isinstance(balance, float) 