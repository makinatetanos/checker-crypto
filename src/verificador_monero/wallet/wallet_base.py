"""
Clase base para wallets.
"""

from abc import ABC, abstractmethod
from typing import Optional

class WalletError(Exception):
    """
    Excepción base para errores de wallet.
    """
    pass

class WalletBase(ABC):
    """
    Clase abstracta base para wallets.
    Define la interfaz mínima que debe implementar cualquier wallet.
    """
    
    def __init__(self, address: Optional[str] = None, seed: Optional[str] = None) -> None:
        """
        Inicializa la wallet.

        Args:
            address (Optional[str]): Dirección de la wallet.
            seed (Optional[str]): Seed de la wallet.
        """
        """
        Inicializa la wallet.
        
        Args:
            address: Dirección de la wallet.
            seed: Seed de la wallet.
        """
        self._address = address
        self._seed = seed
    
    @property
    def address(self) -> str:
        """
        Obtiene la dirección de la wallet.

        Returns:
            str: Dirección de la wallet.
        Raises:
            WalletError: Si la wallet no tiene dirección.
        """
        if not self._address:
            raise WalletError("La wallet no tiene dirección")
        return self._address
    
    @property
    def seed(self) -> Optional[str]:
        """
        Obtiene la seed de la wallet.

        Returns:
            Optional[str]: Seed de la wallet (o None si no está definida).
        """
        return self._seed
    
    @abstractmethod
    def refresh(self) -> None:
        """
        Actualiza el estado de la wallet.
        """
        pass
    
    @abstractmethod
    def check_balance(self) -> float:
        """
        Verifica el balance de la wallet.

        Returns:
            float: El balance en XMR.
        """
        pass
    
    @abstractmethod
    def is_lost(self) -> bool:
        """
        Verifica si la wallet está perdida.

        Returns:
            bool: True si la wallet está perdida.
        """
        pass 