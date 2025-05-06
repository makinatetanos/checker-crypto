import pytest
import threading
from verificador_monero.wallet.monero_wallet import MoneroWallet
import time

# Stress test: escaneo concurrente de muchas wallets

def scan_wallet(wallet, results, idx):
    try:
        wallet.refresh()
        results[idx] = wallet._balance
    except Exception as e:
        results[idx] = str(e)

def test_concurrent_wallet_scans():
    n_wallets = 20  # Puedes subir este número si tu máquina lo permite
    wallets = [MoneroWallet(test_mode=True) for _ in range(n_wallets)]
    threads = []
    results = [None] * n_wallets

    for i, wallet in enumerate(wallets):
        t = threading.Thread(target=scan_wallet, args=(wallet, results, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Todos los resultados deben ser 1.0 en modo test
    assert all(r == 1.0 for r in results)

# Opcional: Stress test con sleep y comprobación de race conditions
def test_concurrent_wallet_scans_with_delay():
    n_wallets = 10
    wallets = [MoneroWallet(test_mode=True) for _ in range(n_wallets)]
    threads = []
    results = [None] * n_wallets

    def delayed_scan(wallet, results, idx):
        time.sleep(0.05 * idx)  # Escalonado
        scan_wallet(wallet, results, idx)

    for i, wallet in enumerate(wallets):
        t = threading.Thread(target=delayed_scan, args=(wallet, results, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert all(r == 1.0 for r in results)
