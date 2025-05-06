import os
import random
import string
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

def generate_seed(length: int = 64) -> str:
    """Genera una semilla aleatoria segura."""
    if length < 32:
        raise ValueError("Seed length must be at least 32 characters")
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

def validate_monero_address(address: str) -> bool:
    """Valida una dirección Monero."""
    if not address:
        return False
    if not address.startswith('4'):
        return False
    if len(address) != 95:
        return False
    return all(c in string.hexdigits for c in address[1:])

def format_balance(balance: float) -> str:
    """Formatea un balance de Monero."""
    return f"{balance:.12f} XMR"

def format_timestamp(timestamp: int) -> str:
    """Formatea un timestamp Unix a una fecha legible."""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def get_data_dir() -> Path:
    """Obtiene el directorio de datos."""
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    data_dir.mkdir(exist_ok=True)
    return data_dir

def get_log_dir() -> Path:
    """Obtiene el directorio de logs."""
    log_dir = Path(os.getenv("LOG_DIR", "logs"))
    log_dir.mkdir(exist_ok=True)
    return log_dir

def setup_directories() -> None:
    """Configura los directorios necesarios."""
    get_data_dir()
    get_log_dir()

def get_timestamp() -> int:
    """Obtiene el timestamp actual en segundos."""
    return int(time.time())

def format_duration(seconds: int) -> str:
    """Formatea una duración en segundos a un formato legible."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def format_size(size_bytes: int) -> str:
    """Formatea un tamaño en bytes a un formato legible."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def get_file_size(file_path: str) -> Optional[int]:
    """Obtiene el tamaño de un archivo en bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return None

def is_valid_file_path(file_path: str) -> bool:
    """Verifica si una ruta de archivo es válida."""
    try:
        Path(file_path).resolve()
        return True
    except (OSError, RuntimeError):
        return False 