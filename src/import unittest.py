import unittest
from src.blockchain_api import obtener_datos_blockchain

class TestBlockchainApi(unittest.TestCase):
    def test_obtener_datos_blockchain(self):
        resultado = obtener_datos_blockchain()
        self.assertIn("Conexión", resultado)