import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

@dataclass
class MoneroConfig:
    rpc_host: str = "localhost"
    rpc_port: str = "18081"
    test_mode: bool = True
    max_threads: int = 4
    scan_interval_ms: int = 1000
    max_attempts: int = 1000
    encryption_key: Optional[str] = None
    data_dir: str = "data"
    log_dir: str = "logs"

    def __post_init__(self):
        if not self.rpc_host or not self.rpc_port:
            raise ValueError("RPC host and port are required")
        if self.max_threads < 1:
            raise ValueError("max_threads must be at least 1")
        if self.scan_interval_ms < 100:
            raise ValueError("scan_interval_ms must be at least 100")
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

    def get_rpc_url(self) -> str:
        return f"http://{self.rpc_host}:{self.rpc_port}/json_rpc"

    def validate(self) -> bool:
        try:
            self.__post_init__()
            return True
        except ValueError:
            return False

    @classmethod
    def load_config(cls, test_mode: bool = True) -> 'MoneroConfig':
        load_dotenv()
        
        config = cls(
            rpc_host=os.getenv("MONERO_RPC_HOST", "localhost"),
            rpc_port=os.getenv("MONERO_RPC_PORT", "18081"),
            test_mode=test_mode or os.getenv("TEST_MODE", "true").lower() == "true",
            max_threads=int(os.getenv("MAX_THREADS", "4")),
            scan_interval_ms=int(os.getenv("SCAN_INTERVAL_MS", "1000")),
            max_attempts=int(os.getenv("MAX_ATTEMPTS", "1000")),
            encryption_key=os.getenv("ENCRYPTION_KEY"),
            data_dir=os.getenv("DATA_DIR", "data"),
            log_dir=os.getenv("LOG_DIR", "logs")
        )

        if not config.validate():
            raise ValueError("Invalid configuration")

        return config

    def setup_directories(self) -> None:
        Path(self.data_dir).mkdir(exist_ok=True)
        Path(self.log_dir).mkdir(exist_ok=True) 