import requests
import json
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class MoneroBlockchainAPI:
    def __init__(self):
        self.base_url = "https://xmrchain.net/api"
        self.daemon_url = "https://node.moneroworld.com:18089/json_rpc"
        
    def get_block_height(self) -> int:
        """Obtiene la altura actual de la blockchain"""
        try:
            response = requests.get(f"{self.base_url}/networkinfo")
            if response.status_code != 200:
                raise Exception(f"Error de API: {response.status_code}")
            return response.json()['height']
        except Exception as e:
            logger.error(f"Error al obtener altura del bloque: {str(e)}")
            return 0
            
    def get_transaction_info(self, tx_hash: str) -> Dict:
        """Obtiene información detallada de una transacción"""
        try:
            response = requests.get(f"{self.base_url}/transaction/{tx_hash}")
            if response.status_code != 200:
                raise Exception(f"Error de API: {response.status_code}")
            return response.json()
        except Exception as e:
            logger.error(f"Error al obtener información de transacción: {str(e)}")
            return {}
            
    def get_mempool_transactions(self) -> List[Dict]:
        """Obtiene las transacciones en el mempool"""
        try:
            response = requests.get(f"{self.base_url}/mempool")
            if response.status_code != 200:
                raise Exception(f"Error de API: {response.status_code}")
            data = response.json()
            return data.get('transactions', [])
        except Exception as e:
            logger.error(f"Error al obtener transacciones del mempool: {str(e)}")
            return []
            
    def get_block_info(self, block_height: int) -> Dict:
        """Obtiene información de un bloque específico"""
        try:
            response = requests.get(f"{self.base_url}/block/{block_height}")
            if response.status_code != 200:
                raise Exception(f"Error de API: {response.status_code}")
            return response.json()
        except Exception as e:
            logger.error(f"Error al obtener información del bloque: {str(e)}")
            return {}
            
    def get_network_stats(self) -> Dict:
        """Obtiene estadísticas de la red Monero"""
        try:
            response = requests.get(f"{self.base_url}/networkinfo")
            if response.status_code != 200:
                raise Exception(f"Error de API: {response.status_code}")
            data = response.json()
            return {
                'height': data.get('height', 0),
                'hash_rate': data.get('hash_rate', 0),
                'tx_count': data.get('tx_count', 0),
                'difficulty': data.get('difficulty', 0)
            }
        except Exception as e:
            logger.error(f"Error al obtener estadísticas de red: {str(e)}")
            return {
                'height': 0,
                'hash_rate': 0,
                'tx_count': 0,
                'difficulty': 0
            }
            
    def get_address_transactions(self, address: str, view_key: Optional[str] = None) -> List[Dict]:
        """Obtiene las transacciones asociadas a una dirección"""
        try:
            params = {
                "address": address
            }
            if view_key:
                params["viewkey"] = view_key
                
            response = requests.get(f"{self.base_url}/outputs", params=params)
            if response.status_code != 200:
                raise Exception(f"Error de API: {response.status_code}")
            data = response.json()
            return data.get('outputs', [])
        except Exception as e:
            logger.error(f"Error al obtener transacciones de la dirección: {str(e)}")
            return []
            
    def get_wallet_balance(self, address: str, view_key: Optional[str] = None) -> float:
        """Calcula el balance aproximado de una wallet basado en sus transacciones"""
        try:
            transactions = self.get_address_transactions(address, view_key)
            balance = sum(tx.get('amount', 0) for tx in transactions)
            return balance / 1e12  # Convertir de piconero a XMR
        except Exception as e:
            logger.error(f"Error al calcular balance de wallet: {str(e)}")
            return 0.0