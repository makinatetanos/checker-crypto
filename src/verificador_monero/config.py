"""
Configuración de la aplicación.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class MoneroConfig:
    """Configuración para la conexión con Monero."""
    rpc_host: str = "localhost"
    rpc_port: str = "18081"
    rpc_user: str = ""
    rpc_password: str = ""
    encryption_key: Optional[str] = None

def load_config(test_mode: bool = False) -> MoneroConfig:
    """
    Carga la configuración de la aplicación.
    
    Args:
        test_mode: Si es True, se usa configuración de prueba.
        
    Returns:
        MoneroConfig: La configuración cargada.
    """
    if test_mode:
        return MoneroConfig()
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener configuración
    config = MoneroConfig(
        rpc_host=os.getenv("MONERO_RPC_HOST", "localhost"),
        rpc_port=os.getenv("MONERO_RPC_PORT", "18081"),
        rpc_user=os.getenv("MONERO_RPC_USER", ""),
        rpc_password=os.getenv("MONERO_RPC_PASSWORD", ""),
        encryption_key=os.getenv("ENCRYPTION_KEY")
    )
    
    return config

def get_data_dir() -> Path:
    """
    Obtiene el directorio de datos de la aplicación.
    
    Returns:
        Path: El directorio de datos.
    """
    # En Windows: %APPDATA%/VerificadorMonero
    # En Linux: ~/.verificador_monero
    # En macOS: ~/Library/Application Support/VerificadorMonero
    if os.name == 'nt':  # Windows
        base_dir = os.getenv('APPDATA')
        if not base_dir:
            base_dir = os.path.expanduser('~')
        data_dir = Path(base_dir) / 'VerificadorMonero'
    elif os.name == 'posix':  # Linux/macOS
        if os.path.exists('/Applications'):  # macOS
            data_dir = Path.home() / 'Library/Application Support/VerificadorMonero'
        else:  # Linux
            data_dir = Path.home() / '.verificador_monero'
    else:
        data_dir = Path.home() / '.verificador_monero'
    
    # Crear el directorio si no existe
    data_dir.mkdir(parents=True, exist_ok=True)
    
    return data_dir 