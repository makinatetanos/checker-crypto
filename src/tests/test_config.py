import pytest
import os
from ..config import MoneroConfig

def test_config_default_values():
    config = MoneroConfig()
    assert config.rpc_host == "localhost"
    assert config.rpc_port == "18081"
    assert config.test_mode is True
    assert config.max_threads > 0
    assert config.scan_interval_ms > 0
    assert config.max_attempts > 0

def test_config_validation():
    # Valores válidos
    config = MoneroConfig(
        rpc_host="localhost",
        rpc_port="18081",
        max_threads=4,
        scan_interval_ms=1000,
        max_attempts=1000
    )
    assert config.validate()

    # Valores inválidos
    with pytest.raises(ValueError):
        MoneroConfig(max_threads=0)
    with pytest.raises(ValueError):
        MoneroConfig(scan_interval_ms=50)
    with pytest.raises(ValueError):
        MoneroConfig(max_attempts=0)

def test_config_rpc_url():
    config = MoneroConfig(
        rpc_host="localhost",
        rpc_port="18081"
    )
    assert config.get_rpc_url() == "http://localhost:18081/json_rpc"

def test_config_load_from_env(monkeypatch):
    monkeypatch.setenv("MONERO_RPC_HOST", "test_host")
    monkeypatch.setenv("MONERO_RPC_PORT", "12345")
    monkeypatch.setenv("TEST_MODE", "false")
    monkeypatch.setenv("MAX_THREADS", "8")
    monkeypatch.setenv("SCAN_INTERVAL_MS", "2000")
    monkeypatch.setenv("MAX_ATTEMPTS", "5000")
    monkeypatch.setenv("ENCRYPTION_KEY", "test_key")
    monkeypatch.setenv("DATA_DIR", "test_data")
    monkeypatch.setenv("LOG_DIR", "test_logs")

    config = MoneroConfig.load_config()
    assert config.rpc_host == "test_host"
    assert config.rpc_port == "12345"
    assert config.test_mode is False
    assert config.max_threads == 8
    assert config.scan_interval_ms == 2000
    assert config.max_attempts == 5000
    assert config.encryption_key == "test_key"
    assert config.data_dir == "test_data"
    assert config.log_dir == "test_logs"

def test_config_setup_directories(tmp_path):
    config = MoneroConfig(
        data_dir=str(tmp_path / "data"),
        log_dir=str(tmp_path / "logs")
    )
    config.setup_directories()
    assert (tmp_path / "data").exists()
    assert (tmp_path / "logs").exists()
    assert (tmp_path / "data").is_dir()
    assert (tmp_path / "logs").is_dir()

def test_config_test_mode_override():
    config = MoneroConfig.load_config(test_mode=False)
    assert config.test_mode is False

def test_config_encryption_key():
    config = MoneroConfig(encryption_key="test_key")
    assert config.encryption_key == "test_key"
    assert config.validate() 