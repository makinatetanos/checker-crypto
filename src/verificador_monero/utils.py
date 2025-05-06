"""
Utilidades generales para el manejo de cifrado, logging y validación de direcciones en el verificador de wallets Monero.
"""

import logging
import base64
from pathlib import Path
from typing import Optional, Callable, Any
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from logging.handlers import RotatingFileHandler
from functools import wraps
from .config import get_data_dir

def handle_gui_errors(fallback: Callable[[Exception], None]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorador para centralizar el manejo de errores en métodos de GUI.
    Loguea la excepción y ejecuta una función de fallback (por ejemplo, emitir señal o mostrar mensaje).

    Args:
        fallback (Callable[[Exception], None]): Función a ejecutar en caso de excepción.

    Returns:
        Callable: Decorador que envuelve la función objetivo.
    """
    """
    Decorador para centralizar el manejo de errores en métodos de GUI.
    Loguea la excepción y ejecuta una función de fallback (por ejemplo, emitir señal o mostrar mensaje).
    
    Args:
        fallback: función que recibe la excepción y maneja el error (mostrar mensaje, emitir señal, etc).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.getLogger('verificador_monero').error(f"Error en {func.__name__}: {str(e)}")
                fallback(e)
        return wrapper
    return decorator

def setup_logging(debug: bool = False) -> None:
    """
    Configura el logging de la aplicación, con rotación de logs y nivel ajustable.

    Args:
        debug (bool): Si es True, activa el nivel DEBUG.
    """
    """
    Configura el sistema de logging con rotación de archivos.
    
    Args:
        debug: Si es True, se usa nivel DEBUG.
    """
    level = logging.DEBUG if debug else logging.INFO
    log_dir = get_data_dir() / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'verificador.log'
    
    # Configurar el formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # Configurar el manejador de archivo con rotación
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Configurar el manejador de consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configurar el logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Crear logger específico para la aplicación
    app_logger = logging.getLogger('verificador_monero')
    app_logger.info('Iniciando aplicación Verificador Monero')

def encrypt_data(data: str, key: str) -> bytes:
    """
    Cifra una cadena de texto usando una clave dada.

    Args:
        data (str): Datos a cifrar.
        key (str): Clave de cifrado.

    Returns:
        bytes: Datos cifrados.
    """
    """
    Encripta datos usando Fernet.
    
    Args:
        data: Los datos a encriptar.
        key: La clave de encriptación.
        
    Returns:
        bytes: Los datos encriptados.
        
    Raises:
        ValueError: Si los datos o la clave son inválidos.
    """
    if not data or not key:
        raise ValueError("Los datos y la clave no pueden estar vacíos")
    
    try:
        # Derivar una clave compatible con Fernet
        salt = b"monero_salt"  # Salt fijo para la derivación
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        # Convertir la clave a bytes si es necesario
        if isinstance(key, str):
            key_bytes = key.encode()
        else:
            key_bytes = key
            
        fernet_key = base64.urlsafe_b64encode(kdf.derive(key_bytes))
        fernet = Fernet(fernet_key)
        
        # Encriptar los datos
        return fernet.encrypt(data.encode())
    except Exception as e:
        raise ValueError(f"Error al encriptar los datos: {str(e)}")

def decrypt_data(encrypted_data: bytes, key: str) -> str:
    """
    Descifra datos cifrados usando una clave dada.

    Args:
        encrypted_data (bytes): Datos cifrados.
        key (str): Clave de cifrado.

    Returns:
        str: Datos descifrados como texto plano.
    """
    """
    Desencripta datos usando Fernet.
    
    Args:
        encrypted_data: Los datos encriptados.
        key: La clave de encriptación.
        
    Returns:
        str: Los datos desencriptados.
        
    Raises:
        ValueError: Si los datos o la clave son inválidos.
    """
    if not encrypted_data or not key:
        raise ValueError("Los datos encriptados y la clave no pueden estar vacíos")
    
    try:
        # Derivar una clave compatible con Fernet
        salt = b"monero_salt"  # Salt fijo para la derivación
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        # Convertir la clave a bytes si es necesario
        if isinstance(key, str):
            key_bytes = key.encode()
        else:
            key_bytes = key
            
        fernet_key = base64.urlsafe_b64encode(kdf.derive(key_bytes))
        fernet = Fernet(fernet_key)
        
        # Desencriptar los datos
        return fernet.decrypt(encrypted_data).decode()
    except InvalidToken:
        raise ValueError("Los datos encriptados no son válidos o la clave es incorrecta")
    except Exception as e:
        raise ValueError(f"Error al desencriptar los datos: {str(e)}")

def validate_monero_address(address: Optional[str]) -> bool:
    """
    Valida si una dirección de Monero tiene el formato correcto.

    Args:
        address (Optional[str]): Dirección a validar.

    Returns:
        bool: True si la dirección es válida.
    """
    """
    Valida una dirección de Monero.
    
    Args:
        address: La dirección a validar.
        
    Returns:
        bool: True si la dirección es válida.
    """
    if not isinstance(address, str):
        return False
    
    # Verificar longitud básica (95 caracteres para direcciones estándar)
    if len(address) != 95:
        return False
    
    # Verificar que comienza con '4'
    if not address.startswith('4'):
        return False
    
    # Verificar caracteres válidos (base58)
    valid_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
    return all(c in valid_chars for c in address) 