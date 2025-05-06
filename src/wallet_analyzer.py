import logging
from typing import Dict, List, Optional
from src.monero_handler import MoneroHandler

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WalletAnalyzer:
    def __init__(self, monero_handler: Optional[MoneroHandler] = None):
        """
        Inicializa el analizador de wallets.
        
        Args:
            monero_handler: Instancia opcional de MoneroHandler. Si no se proporciona,
                          se creará una nueva instancia en modo de prueba.
        """
        self.monero_handler = monero_handler or MoneroHandler(test_mode=True)
        self.resultados: Dict[str, Dict] = {}

    def analizar_wallet(self, direccion: str) -> Dict:
        """
        Analiza una wallet específica.
        
        Args:
            direccion: La dirección de la wallet a analizar.
            
        Returns:
            Dict con los resultados del análisis.
        """
        try:
            if not self.monero_handler.validate_address(direccion):
                raise ValueError("Dirección de wallet inválida")

            balance = self.monero_handler.check_wallet_balance(direccion)
            esta_perdida = self.monero_handler.is_wallet_lost(direccion)

            resultado = {
                "direccion": direccion,
                "balance": balance,
                "esta_perdida": esta_perdida,
                "estado": "perdida" if esta_perdida else "activa",
                "error": None
            }

            self.resultados[direccion] = resultado
            return resultado

        except Exception as e:
            logger.error(f"Error al analizar wallet {direccion}: {str(e)}")
            resultado = {
                "direccion": direccion,
                "balance": None,
                "esta_perdida": None,
                "estado": "error",
                "error": str(e)
            }
            self.resultados[direccion] = resultado
            return resultado

    def analizar_multiple_wallets(self, direcciones: List[str]) -> List[Dict]:
        """
        Analiza múltiples wallets.
        
        Args:
            direcciones: Lista de direcciones a analizar.
            
        Returns:
            Lista de diccionarios con los resultados del análisis.
        """
        return [self.analizar_wallet(dir) for dir in direcciones]

    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas de los análisis realizados.
        
        Returns:
            Dict con estadísticas generales.
        """
        total_wallets = len(self.resultados)
        wallets_perdidas = sum(1 for r in self.resultados.values() if r["estado"] == "perdida")
        wallets_activas = sum(1 for r in self.resultados.values() if r["estado"] == "activa")
        wallets_error = sum(1 for r in self.resultados.values() if r["estado"] == "error")
        balance_total = sum(r["balance"] or 0 for r in self.resultados.values())

        return {
            "total_wallets": total_wallets,
            "wallets_perdidas": wallets_perdidas,
            "wallets_activas": wallets_activas,
            "wallets_error": wallets_error,
            "balance_total": balance_total
        }

    def limpiar_resultados(self) -> None:
        """Limpia los resultados almacenados."""
        self.resultados.clear()