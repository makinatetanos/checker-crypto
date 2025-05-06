import os
import time
import requests
import logging
from monero.wallet import Wallet
from monero.seed import Seed
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MoneroHandlerError(Exception):
    """Excepción personalizada para errores del MoneroHandler"""
    pass

class MoneroHandler:
    def __init__(self, test_mode=False):
        try:
            load_dotenv()
            self.encryption_key = os.getenv('ENCRYPTION_KEY')
            if not self.encryption_key:
                self.encryption_key = Fernet.generate_key()
                # Guardar la clave generada en el archivo .env
                with open('.env', 'a', encoding='utf-8') as f:
                    f.write(f'\nENCRYPTION_KEY={self.encryption_key.decode()}')
            self.cipher_suite = Fernet(self.encryption_key)
            
            # Configuración de Monero RPC
            self.rpc_host = os.getenv('MONERO_RPC_HOST', 'localhost')
            self.rpc_port = os.getenv('MONERO_RPC_PORT', '18081')
            self.rpc_user = os.getenv('MONERO_RPC_USER', '')
            self.rpc_password = os.getenv('MONERO_RPC_PASSWORD', '')
            self.test_mode = test_mode
            self.last_request_time = 0
            
            if not self.test_mode:
                # Solo inicializar la wallet si no estamos en modo prueba
                self.wallet = Wallet(
                    host=self.rpc_host,
                    port=self.rpc_port,
                    password=self.rpc_password
                )
            
            logger.info(f"Inicializando MoneroHandler en {self.rpc_host}:{self.rpc_port}")
            
        except Exception as e:
            logger.error(f"Error al inicializar MoneroHandler: {str(e)}")
            raise MoneroHandlerError(f"Error al inicializar MoneroHandler: {str(e)}")

    def _rate_limit(self):
        """Implementa rate limiting para las llamadas a la API."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < 1:  # 1 segundo entre llamadas
            time.sleep(1 - time_since_last_request)
        self.last_request_time = time.time()

    def generate_seed(self):
        """Genera una nueva frase semilla de Monero."""
        try:
            seed = Seed()
            return seed.phrase
        except Exception as e:
            logger.error(f"Error al generar seed: {str(e)}")
            raise MoneroHandlerError(f"Error al generar seed: {str(e)}")

    def create_wallet(self, seed=None):
        """Crea una nueva wallet de Monero."""
        try:
            if seed is None:
                seed = self.generate_seed()
            elif not isinstance(seed, str) or not seed.strip():
                raise ValueError("La seed debe ser una cadena de texto no vacía")
            elif len(seed.split()) < 12:  # Las seeds de Monero tienen al menos 12 palabras
                raise ValueError("Formato de seed inválido")
            
            if self.test_mode:
                # En modo prueba, retornar una dirección de prueba
                class TestWallet:
                    def address(self):
                        return '44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A'
                return TestWallet()
            
            # En modo real, aquí iría la lógica para crear la wallet
            raise NotImplementedError("Funcionalidad no implementada para modo real")
            
        except Exception as e:
            logger.error(f"Error al crear wallet: {str(e)}")
            raise MoneroHandlerError(f"Error al crear wallet: {str(e)}")

    def encrypt_seed(self, seed):
        """Encripta la frase semilla para almacenamiento seguro."""
        try:
            if not isinstance(seed, str):
                raise ValueError("La seed debe ser una cadena de texto")
            if not seed.strip():
                raise ValueError("La seed no puede estar vacía")
            return self.cipher_suite.encrypt(seed.encode())
        except Exception as e:
            logger.error(f"Error al encriptar seed: {str(e)}")
            raise MoneroHandlerError(f"Error al encriptar seed: {str(e)}")

    def decrypt_seed(self, encrypted_seed):
        """Desencripta la frase semilla almacenada."""
        try:
            if not isinstance(encrypted_seed, bytes):
                raise ValueError("La seed encriptada debe ser bytes")
            return self.cipher_suite.decrypt(encrypted_seed).decode()
        except Exception as e:
            logger.error(f"Error al desencriptar seed: {str(e)}")
            raise MoneroHandlerError(f"Error al desencriptar seed: {str(e)}")

    def check_wallet_balance(self, address):
        """Verifica el balance de una wallet de Monero."""
        try:
            if not self.validate_address(address):
                raise ValueError("Dirección de Monero inválida")

            if self.test_mode:
                # En modo prueba, retornar un balance de prueba
                self._rate_limit()  # Aplicar rate limiting incluso en modo prueba
                return 1.23456789

            # Usar el explorador de Monero para verificar el balance
            self._rate_limit()
            response = requests.get(
                f"https://api.monero.ws/address/{address}/balance",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return float(data.get('balance', 0)) / 1e12  # Convertir a XMR
                
        except Exception as e:
            logger.error(f"Error al verificar balance: {str(e)}")
            raise MoneroHandlerError(f"Error al verificar balance: {str(e)}")

    def is_wallet_lost(self, address):
        """Determina si una wallet está perdida basándose en ciertos criterios."""
        try:
            if not self.validate_address(address):
                raise ValueError("Dirección de Monero inválida")

            if self.test_mode:
                # En modo prueba, retornar un resultado de prueba
                self._rate_limit()  # Aplicar rate limiting incluso en modo prueba
                return True

            # Usar el explorador de Monero para verificar las transacciones
            self._rate_limit()
            response = requests.get(
                f"https://api.monero.ws/address/{address}/transactions",
                timeout=10
            )
            response.raise_for_status()
            transactions = response.json()
            
            if not transactions:
                return True
                
            last_tx_time = max(tx['timestamp'] for tx in transactions)
            two_years_ago = time.time() - (2 * 365 * 24 * 60 * 60)
            
            return last_tx_time < two_years_ago
                
        except Exception as e:
            logger.error(f"Error al verificar estado de wallet: {str(e)}")
            raise MoneroHandlerError(f"Error al verificar estado de wallet: {str(e)}")

    def validate_address(self, address):
        """Valida si una dirección de Monero es válida."""
        try:
            if not isinstance(address, str):
                return False
                
            # Validación básica de dirección Monero
            if len(address) != 95 or not address.startswith('4'):
                return False
                
            # Aquí se podría agregar validación más específica
            # como verificar el checksum, etc.
            
            return True
        except Exception as e:
            logger.error(f"Error al validar dirección: {str(e)}")
            raise MoneroHandlerError(f"Error al validar dirección: {str(e)}")