import sys
from pathlib import Path

# Agregar el directorio src al path de Python
sys.path.append(str(Path(__file__).parent.parent))

from src.monero_handler import MoneroHandler
from src.wallet_analyzer import WalletAnalyzer
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def probar_monero_handler():
    print("\n=== Probando MoneroHandler ===")
    handler = MoneroHandler(test_mode=True)
    
    # Generar una seed
    seed = handler.generate_seed()
    print(f"\nSeed generada: {seed}")
    
    # Crear una wallet
    wallet = handler.create_wallet()
    direccion = wallet.address()
    print(f"\nDirección de wallet: {direccion}")
    
    # Verificar balance
    balance = handler.check_wallet_balance(direccion)
    print(f"\nBalance de la wallet: {balance} XMR")
    
    # Verificar si está perdida
    esta_perdida = handler.is_wallet_lost(direccion)
    print(f"\n¿La wallet está perdida?: {esta_perdida}")
    
    # Encriptar y desencriptar seed
    encrypted = handler.encrypt_seed(seed)
    decrypted = handler.decrypt_seed(encrypted)
    print(f"\nSeed original: {seed}")
    print(f"Seed encriptada: {encrypted}")
    print(f"Seed desencriptada: {decrypted}")
    print(f"¿Las seeds coinciden?: {seed == decrypted}")

def probar_wallet_analyzer():
    print("\n=== Probando WalletAnalyzer ===")
    analyzer = WalletAnalyzer()
    
    # Lista de direcciones de prueba
    direcciones = [
        "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A",
        "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3B",
        "direccion_invalida"  # Esta debería fallar
    ]
    
    # Analizar múltiples wallets
    print("\nAnalizando múltiples wallets...")
    resultados = analyzer.analizar_multiple_wallets(direcciones)
    
    # Mostrar resultados individuales
    print("\nResultados del análisis:")
    for resultado in resultados:
        print(f"\nDirección: {resultado['direccion']}")
        print(f"Estado: {resultado['estado']}")
        print(f"Balance: {resultado['balance']} XMR")
        if resultado['error']:
            print(f"Error: {resultado['error']}")
    
    # Mostrar estadísticas
    print("\nEstadísticas generales:")
    stats = analyzer.obtener_estadisticas()
    for key, value in stats.items():
        print(f"{key}: {value}")

def main():
    try:
        print("Iniciando pruebas del programa...")
        
        # Probar MoneroHandler
        probar_monero_handler()
        
        # Probar WalletAnalyzer
        probar_wallet_analyzer()
        
        print("\nPruebas completadas exitosamente!")
        
    except Exception as e:
        logger.error(f"Error durante las pruebas: {str(e)}")
        raise

if __name__ == "__main__":
    main() 