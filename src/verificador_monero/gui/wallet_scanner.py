"""
Scanner de wallets Monero.
"""

import logging
from PyQt6.QtCore import QThread, pyqtSignal
from ..monero_handler import MoneroHandler

logger = logging.getLogger('verificador_monero.scanner')

class WalletScanner(QThread):
    """
    Clase encargada de escanear posibles wallets de Monero.
    Ejecuta el proceso en un hilo separado y comunica progreso y errores mediante señales Qt.
    """
    
    # Señales
    progress_updated = pyqtSignal(int)
    wallet_found = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, test_mode: bool = True) -> None:
        """
        Inicializa el scanner de wallets.

        Args:
            test_mode (bool): Si es True, ejecuta el escaneo en modo de prueba.
        """
        """
        Inicializa el scanner.
        
        Args:
            test_mode: Si es True, se ejecuta en modo de prueba.
        """
        super().__init__()
        self.is_running = True
        self.test_mode = test_mode
        logger.info(f"Inicializando scanner (test_mode={test_mode})")
        try:
            self.monero_handler = MoneroHandler(test_mode=test_mode)
        except Exception as e:
            logger.error(f"Error al inicializar MoneroHandler: {str(e)}")
            raise

    def run(self) -> None:
        """
        Ejecuta el escaneo de wallets.
        Emite señales de progreso, wallets encontradas y errores.
        """
        """Ejecuta el escaneo de wallets."""
        try:
            logger.info("Iniciando proceso de escaneo")
            total_attempts = 1000
            for i in range(total_attempts):
                if not self.is_running:
                    logger.info("Escaneo detenido por el usuario")
                    break
                try:
                    logger.debug(f"Intento {i+1}/{total_attempts}")
                    wallet = self.monero_handler.create_wallet()
                    address = wallet.address()
                    if self.monero_handler.is_wallet_lost(address):
                        balance = self.monero_handler.check_wallet_balance(address)
                        if balance > 0:
                            seed = self.monero_handler.generate_seed()
                            wallet_info = f"Wallet encontrada:\nDirección: {address}\nBalance: {balance} XMR\nSeed: {seed}\n"
                            logger.info(f"Wallet encontrada con balance: {balance} XMR")
                            self.wallet_found.emit(wallet_info)
                    progress = int((i + 1) / total_attempts * 100)
                    self.progress_updated.emit(progress)
                    self.msleep(100)
                except Exception as e:
                    logger.error(f"Error en intento {i+1}: {str(e)}")
                    self.error_occurred.emit(f"Error en intento {i+1}: {str(e)}")
                    continue
            logger.info("Proceso de escaneo completado")
        except Exception as e:
            error_msg = f"Error durante el escaneo: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def stop(self) -> None:
        """
        Detiene el proceso de escaneo de wallets.
        """
        """Detiene el escaneo."""
        logger.info("Deteniendo scanner")
        self.is_running = False 