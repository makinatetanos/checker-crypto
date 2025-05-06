import os
import json
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime
from cryptography.fernet import Fernet
from pathlib import Path
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MoneroWallet:
    address: str
    balance: float
    is_lost: bool = False
    last_checked: Optional[datetime] = None
    private_key: Optional[str] = None

    def __post_init__(self):
        if not self.address.startswith('4'):
            raise ValueError("Invalid Monero address format")
        if len(self.address) != 95:
            raise ValueError("Invalid Monero address length")
        if self.balance < 0:
            raise ValueError("Balance cannot be negative")

class WalletManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.wallets_file = self.data_dir / "wallets.json"
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        self._wallets: Dict[str, MoneroWallet] = {}
        self._setup()

    def _setup(self):
        self.data_dir.mkdir(exist_ok=True)
        if self.wallets_file.exists():
            self._load_wallets()

    def _load_wallets(self):
        try:
            with open(self.wallets_file, 'r') as f:
                data = json.load(f)
                if self.encryption_key:
                    fernet = Fernet(self.encryption_key.encode())
                    data = json.loads(fernet.decrypt(data.encode()))
                self._wallets = {
                    addr: MoneroWallet(**wallet_data)
                    for addr, wallet_data in data.items()
                }
        except Exception as e:
            logger.error(f"Error loading wallets: {e}")
            self._wallets = {}


    def _save_wallets_sync(self):
        try:
            data = {
                addr: {
                    'address': w.address,
                    'balance': w.balance,
                    'is_lost': w.is_lost,
                    'last_checked': w.last_checked.isoformat() if w.last_checked else None,
                    'private_key': w.private_key
                }
                for addr, w in self._wallets.items()
            }
            json_data = json.dumps(data)
            if self.encryption_key:
                fernet = Fernet(self.encryption_key.encode())
                json_data = fernet.encrypt(json_data.encode()).decode()
            with open(self.wallets_file, 'w') as f:
                f.write(json_data)
        except Exception as e:
            logger.error(f"Error saving wallets (sync): {e}")


    def add_wallet_sync(self, wallet: 'MoneroWallet') -> bool:
        try:
            if wallet.address in self._wallets:
                return False
            self._wallets[wallet.address] = wallet
            self._save_wallets_sync()
            return True
        except Exception as e:
            logger.error(f"Error adding wallet: {e}")
            return False







    def check_balance_sync(self, address: str, rpc_url: str) -> Optional[float]:
        try:
            response = requests.post(rpc_url, json={
                "jsonrpc": "2.0",
                "id": "1",
                "method": "get_balance",
                "params": {"address": address}
            })
            if response.status_code == 200:
                data = response.json()
                return float(data.get('result', {}).get('balance', 0)) / 1e12
        except Exception as e:
            logger.error(f"Error checking balance (sync): {e}")
        return None