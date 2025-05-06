import pytest
import os
import time
from datetime import datetime
from pathlib import Path
from ..utils import (
    generate_seed,
    validate_monero_address,
    format_balance,
    format_timestamp,
    get_data_dir,
    get_log_dir,
    setup_directories,
    get_timestamp,
    format_duration,
    format_size,
    get_file_size,
    is_valid_file_path
)

def test_generate_seed():
    # Test longitud mínima
    with pytest.raises(ValueError):
        generate_seed(31)
    
    # Test longitudes válidas
    for length in [32, 64, 128]:
        seed = generate_seed(length)
        assert len(seed) == length
        assert all(c.isprintable() for c in seed)

def test_validate_monero_address():
    # Direcciones válidas
    valid_addresses = [
        "4" + "1" * 94,
        "4" + "2" * 94,
    ]
    for address in valid_addresses:
        assert validate_monero_address(address)

    # Direcciones inválidas
    invalid_addresses = [
        "5" + "1" * 94,  # Prefijo incorrecto
        "4" + "1" * 93,  # Longitud incorrecta
        "4" + "1" * 95,  # Longitud incorrecta
        "",              # Vacía
        None,            # None
        "4" + "G" * 94,  # Caracteres no hexadecimales
    ]
    for address in invalid_addresses:
        assert not validate_monero_address(address)

def test_format_balance():
    test_cases = [
        (0.0, "0.000000000000 XMR"),
        (1.23456789, "1.234567890000 XMR"),
        (1000000.0, "1000000.000000000000 XMR"),
    ]
    for input_value, expected in test_cases:
        assert format_balance(input_value) == expected

def test_format_timestamp():
    test_cases = [
        (1609459200, "2021-01-01 00:00:00"),
        (1640995200, "2022-01-01 00:00:00"),
    ]
    for timestamp, expected in test_cases:
        formatted = format_timestamp(timestamp)
        assert formatted == expected

def test_directory_functions(tmp_path):
    # Test get_data_dir
    data_dir = get_data_dir()
    assert isinstance(data_dir, Path)
    assert data_dir.exists()
    assert data_dir.is_dir()

    # Test get_log_dir
    log_dir = get_log_dir()
    assert isinstance(log_dir, Path)
    assert log_dir.exists()
    assert log_dir.is_dir()

    # Test setup_directories
    test_data_dir = tmp_path / "test_data"
    test_log_dir = tmp_path / "test_logs"
    os.environ["DATA_DIR"] = str(test_data_dir)
    os.environ["LOG_DIR"] = str(test_log_dir)
    setup_directories()
    assert test_data_dir.exists()
    assert test_log_dir.exists()
    assert test_data_dir.is_dir()
    assert test_log_dir.is_dir()

def test_get_timestamp():
    timestamp = get_timestamp()
    assert isinstance(timestamp, int)
    assert timestamp > 0
    assert timestamp <= int(time.time())

def test_format_duration():
    test_cases = [
        (0, "00:00:00"),
        (61, "00:01:01"),
        (3661, "01:01:01"),
        (86400, "24:00:00"),
    ]
    for seconds, expected in test_cases:
        assert format_duration(seconds) == expected

def test_format_size():
    test_cases = [
        (0, "0.00 B"),
        (1024, "1.00 KB"),
        (1024 * 1024, "1.00 MB"),
        (1024 * 1024 * 1024, "1.00 GB"),
    ]
    for size_bytes, expected in test_cases:
        assert format_size(size_bytes) == expected

def test_get_file_size(tmp_path):
    # Test archivo existente
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    assert get_file_size(str(test_file)) == len("test content")

    # Test archivo inexistente
    assert get_file_size(str(tmp_path / "nonexistent.txt")) is None

def test_is_valid_file_path(tmp_path):
    # Test rutas válidas
    valid_paths = [
        str(tmp_path),
        str(tmp_path / "test.txt"),
        str(tmp_path / "subdir" / "test.txt"),
    ]
    for path in valid_paths:
        assert is_valid_file_path(path)

    # Test rutas inválidas
    invalid_paths = [
        "",  # Vacía
        None,  # None
        "C:\\invalid\\path\\*\\file.txt",  # Caracteres inválidos
    ]
    for path in invalid_paths:
        assert not is_valid_file_path(path) 