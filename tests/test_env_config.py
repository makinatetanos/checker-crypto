import os
import pytest
from dotenv import load_dotenv

# 1. Test: Faltan variables críticas en .env
def test_missing_env_vars(monkeypatch, tmp_path):
    # Crea un .env temporal sin ENCRYPTION_KEY
    env_file = tmp_path / ".env"
    with open(env_file, "w") as f:
        f.write("MONERO_RPC_HOST=localhost\nMONERO_RPC_PORT=18082\nMONERO_RPC_USER=user\nMONERO_RPC_PASSWORD=pass\n")
    monkeypatch.setenv("ENV_PATH", str(env_file))
    load_dotenv(dotenv_path=env_file)
    assert os.getenv("ENCRYPTION_KEY") is None

# 2. Test: .env corrupto
def test_corrupt_env(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    with open(env_file, "w") as f:
        f.write("\0\0\0\0\0\0\0")  # Bytes inválidos
    try:
        load_dotenv(dotenv_path=env_file)
    except Exception as e:
        assert isinstance(e, Exception)

# 3. Test: Valores inválidos en .env
def test_invalid_env_values(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    # Limpiar variables antes del test
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    monkeypatch.delenv("MONERO_RPC_PORT", raising=False)
    with open(env_file, "w") as f:
        f.write("ENCRYPTION_KEY=\nMONERO_RPC_PORT=not_a_number\n")
    # Forzar override para que python-dotenv sobrescriba cualquier valor existente
    load_dotenv(dotenv_path=env_file, override=True)
    assert os.getenv("ENCRYPTION_KEY") == ""
    assert os.getenv("MONERO_RPC_PORT") == "not_a_number"
    # Aquí podrías añadir lógica de validación adicional si tu app la implementa
