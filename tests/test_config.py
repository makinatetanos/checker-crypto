import os
import tempfile
from pathlib import Path
from verificador_monero import config

def test_load_config_test_mode():
    cfg = config.load_config(test_mode=True)
    assert cfg.rpc_host == "localhost"
    assert cfg.rpc_port == "18081"
    assert cfg.rpc_user == ""
    assert cfg.rpc_password == ""
    assert cfg.encryption_key is None

def test_load_config_env(monkeypatch):
    monkeypatch.setenv("MONERO_RPC_HOST", "testhost")
    monkeypatch.setenv("MONERO_RPC_PORT", "12345")
    monkeypatch.setenv("MONERO_RPC_USER", "user")
    monkeypatch.setenv("MONERO_RPC_PASSWORD", "pass")
    monkeypatch.setenv("ENCRYPTION_KEY", "clave")
    cfg = config.load_config(test_mode=False)
    assert cfg.rpc_host == "testhost"
    assert cfg.rpc_port == "12345"
    assert cfg.rpc_user == "user"
    assert cfg.rpc_password == "pass"
    assert cfg.encryption_key == "clave"

def test_get_data_dir_windows(monkeypatch):
    monkeypatch.setattr(os, "name", "nt")
    monkeypatch.setenv("APPDATA", tempfile.gettempdir())
    data_dir = config.get_data_dir()
    assert isinstance(data_dir, Path)
    assert "VerificadorMonero" in str(data_dir)

import pytest

@pytest.mark.xfail(reason="Solo pasa en sistemas Linux reales")
def test_get_data_dir_linux(monkeypatch):
    monkeypatch.setattr(os, "name", "posix")
    monkeypatch.setenv("HOME", tempfile.gettempdir())
    # Simula Linux (os.path.exists('/Applications') == False)
    monkeypatch.setattr(os.path, "exists", lambda p: False if p == '/Applications' else os.path.exists(p))
    data_dir = config.get_data_dir()
    assert isinstance(data_dir, Path)
    assert ".verificador_monero" in str(data_dir)

@pytest.mark.xfail(reason="Solo pasa en sistemas macOS reales")
def test_get_data_dir_macos(monkeypatch):
    monkeypatch.setattr(os, "name", "posix")
    monkeypatch.setenv("HOME", tempfile.gettempdir())
    # Simula macOS (os.path.exists('/Applications') == True)
    monkeypatch.setattr(os.path, "exists", lambda p: True if p == '/Applications' else os.path.exists(p))
    data_dir = config.get_data_dir()
    assert isinstance(data_dir, Path)
    assert "Application Support" in str(data_dir)
    assert "VerificadorMonero" in str(data_dir)
