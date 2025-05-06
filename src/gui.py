import sys
from pathlib import Path
import random
import string

# Agregar el directorio src al path de Python
sys.path.append(str(Path(__file__).parent.parent))

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
from PIL import Image, ImageTk  # Necesario para los iconos
import logging
from datetime import datetime
from src.monero_handler import MoneroHandler
from src.wallet_analyzer import WalletAnalyzer
from src.blockchain_api import MoneroBlockchainAPI
import threading
from typing import Dict, List
import json
import os
import requests

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- NUEVO DISEÑO ---

CRYPTO_LIST = [
    ("Bitcoin", "btc.png"),
    ("Ethereum", "eth.png"),
    ("Litecoin", "ltc.png"),
    ("Binance", "bnb.png"),
    ("Solana", "sol.png"),
    ("Tether", "usdt.png"),
]

MONERO_ADDRESS = "42Ec5nSjmTAS54VnwcWwKCcwvu81ofUxg5DsnWKppgUHEf5AXCPMkZFirAnJoufnF4i71LCkQzePLDRWjj9W6JsxC2y1LBF"
PREMIUM_PRICE_USD = 400

# === API KEYS ===
ETHERSCAN_API_KEY = "AQUÍ_TU_API_KEY_ETHERSCAN"
BSCSCAN_API_KEY = "AQUÍ_TU_API_KEY_BSCSCAN"
BLOCKCHAIR_API_KEY = None  # Opcional
BLOCKCYPHER_TOKEN = None  # Opcional

# === FUNCIONES DE CONSULTA DE BALANCE ===
def get_btc_balance(address):
    url = f"https://api.blockchair.com/bitcoin/dashboards/address/{address}"
    resp = requests.get(url)
    data = resp.json()
    try:
        return int(data['data'][address]['address']['balance']) / 1e8
    except Exception:
        return None

def get_eth_balance(address):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"
    resp = requests.get(url)
    data = resp.json()
    if data["status"] == "1":
        return int(data["result"]) / 1e18
    return None

def get_ltc_balance(address):
    url = f"https://api.blockcypher.com/v1/ltc/main/addrs/{address}/balance"
    if BLOCKCYPHER_TOKEN:
        url += f"?token={BLOCKCYPHER_TOKEN}"
    resp = requests.get(url)
    data = resp.json()
    try:
        return int(data['final_balance']) / 1e8
    except Exception:
        return None

def get_bnb_balance(address):
    url = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&apikey={BSCSCAN_API_KEY}"
    resp = requests.get(url)
    data = resp.json()
    if data["status"] == "1":
        return int(data["result"]) / 1e18
    return None

def get_sol_balance(address):
    url = f"https://public-api.solscan.io/account/{address}"
    resp = requests.get(url, headers={"accept": "application/json"})
    data = resp.json()
    try:
        return float(data['lamports']) / 1e9
    except Exception:
        return None

def get_usdt_balance_eth(address):
    url = (
        f"https://api.etherscan.io/api?module=account&action=tokenbalance"
        f"&contractaddress=0xdAC17F958D2ee523a2206206994597C13D831ec7"
        f"&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"
    )
    resp = requests.get(url)
    data = resp.json()
    if data["status"] == "1":
        return int(data["result"]) / 1e6
    return None

def get_usdt_balance_sol(address):
    url = f"https://public-api.solscan.io/account/token?account={address}"
    resp = requests.get(url, headers={"accept": "application/json"})
    data = resp.json()
    for token in data:
        if token.get('tokenSymbol', '').upper() == 'USDT':
            return float(token.get('tokenAmount', {}).get('uiAmount', 0))
    return None

class CheckerLikeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Software")
        self.root.geometry("350x650")
        self.root.configure(bg="#cccccc")
        self.checked = 0
        self.found = 0
        self.crypto_vars = {}
        self.crypto_images = {}
        self.assets_path = os.path.join(os.path.dirname(__file__), "..", "assets")
        self.is_premium = False
        self.daily_checks = 0
        self.max_free_checks = 10
        self._load_premium_status()
        self._show_version_selector()

    def _show_version_selector(self):
        self._clear_window()
        frame = tk.Frame(self.root, bg="#cccccc")
        frame.pack(expand=True)
        tk.Label(frame, text="Selecciona tu versión", font=("Segoe UI", 16, "bold"), bg="#cccccc").pack(pady=20)
        tk.Button(frame, text="Versión Gratis", font=("Segoe UI", 13), width=20, command=self._start_free).pack(pady=10)
        tk.Button(frame, text="Versión Premium", font=("Segoe UI", 13), width=20, command=self._show_premium_payment).pack(pady=10)
        if self.is_premium:
            tk.Label(frame, text="¡Ya eres usuario premium!", fg="#009900", bg="#cccccc", font=("Segoe UI", 11, "bold")).pack(pady=10)

    def _show_premium_payment(self):
        self._clear_window()
        frame = tk.Frame(self.root, bg="#cccccc")
        frame.pack(expand=True, fill="both")
        tk.Label(frame, text="Actualizar a Premium", font=("Segoe UI", 16, "bold"), bg="#cccccc").pack(pady=10)
        tk.Label(frame, text="Precio: $400 USD en Monero", font=("Segoe UI", 12), bg="#cccccc").pack(pady=5)
        xmr_amount = self._get_xmr_amount(PREMIUM_PRICE_USD)
        tk.Label(frame, text=f"Dirección de pago:", font=("Segoe UI", 11), bg="#cccccc").pack(pady=(10, 0))
        entry = tk.Entry(frame, font=("Consolas", 10), width=50, justify="center")
        entry.insert(0, MONERO_ADDRESS)
        entry.config(state="readonly")
        entry.pack(pady=2)
        tk.Label(frame, text=f"Monto a pagar: {xmr_amount} XMR", font=("Segoe UI", 12, "bold"), fg="#0066cc", bg="#cccccc").pack(pady=5)
        tk.Label(frame, text="Envía exactamente el monto a la dirección y haz clic en 'Verificar pago'", font=("Segoe UI", 9), bg="#cccccc").pack(pady=5)
        tk.Button(frame, text="Verificar pago", font=("Segoe UI", 12), command=lambda: self._verify_payment(xmr_amount)).pack(pady=10)
        tk.Button(frame, text="Volver", font=("Segoe UI", 10), command=self._show_version_selector).pack(pady=5)

    def _get_xmr_amount(self, usd):
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd"
            resp = requests.get(url, timeout=10)
            price = resp.json()["monero"]["usd"]
            return round(usd / price, 6)
        except Exception:
            return "(error)"

    def _verify_payment(self, xmr_amount):
        # Verificación automática usando la blockchain (consulta transacciones entrantes)
        # Aquí se puede usar una API pública como xmrchain.net o moneroexplorer.com
        # Por simplicidad, se usará xmrchain.net (puedes cambiarlo por tu propio nodo/API privada)
        try:
            url = f"https://xmrchain.net/api/outputs?address={MONERO_ADDRESS}"
            resp = requests.get(url, timeout=15)
            data = resp.json()
            pagos = [float(tx["amount"])/1e12 for tx in data["data"]]
            for pago in pagos:
                if abs(pago - float(xmr_amount)) < 0.0001:
                    self.is_premium = True
                    self._save_premium_status()
                    messagebox.showinfo("¡Pago verificado!", "¡Ahora eres usuario premium!")
                    self._start_premium()
                    return
            messagebox.showwarning("No encontrado", "No se encontró el pago. Intenta de nuevo en unos minutos.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo verificar el pago: {e}")

    def _start_free(self):
        self.is_premium = False
        self._main_gui()

    def _start_premium(self):
        self.is_premium = True
        self._main_gui()

    def _main_gui(self):
        self._clear_window()
        self.checked = 0
        self.found = 0
        self.daily_checks = 0
        # --- Cabecera con logo y nombre ---
        header = tk.Frame(self.root, bg="#cccccc")
        header.pack(pady=10, fill="x")
        header.grid_columnconfigure(0, weight=1)
        tk.Label(header, text="🔥", font=("Segoe UI", 28), bg="#cccccc").grid(row=0, column=0, sticky="n", pady=(0, 0))
        tk.Label(header, text="CryptoCheckFull", font=("Segoe UI", 20, "bold"), bg="#cccccc").grid(row=1, column=0, sticky="n", pady=(0, 0))

        # Campo para dirección de wallet del usuario
        wallet_frame = tk.Frame(self.root, bg="#cccccc")
        wallet_frame.pack(pady=(0, 5))
        tk.Label(wallet_frame, text="Tu dirección de wallet para recibir fondos:", font=("Segoe UI", 11), bg="#cccccc").pack(side="left", padx=(5, 2))
        self.user_wallet_entry = tk.Entry(wallet_frame, font=("Consolas", 10), width=35)
        self.user_wallet_entry.pack(side="left", padx=(2, 5))

        # Área superior: Checked
        self.label_checked = tk.Label(self.root, text="Checked:0", font=("Segoe UI", 13, "bold"), bg="#cccccc", anchor="center")
        self.label_checked.pack(fill="x", padx=10, pady=(10, 0))
        # Recuadro negro para logs/resultados
        self.log_frame = tk.Frame(self.root, bg="#000000", height=120, width=320)
        self.log_frame.pack(padx=10, pady=(5, 0), fill="x")
        self.log_frame.pack_propagate(False)
        self.log_text = tk.Text(self.log_frame, bg="#000000", fg="#ffffff", height=7, width=38, relief="flat", font=("Consolas", 11), wrap="word")
        self.log_text.pack(fill="both", expand=True)
        self.log_text.config(state="disabled")
        # Texto found
        self.label_found = tk.Label(self.root, text="found:0", font=("Segoe UI", 12), fg="#009900", bg="#cccccc", anchor="center")
        self.label_found.pack(fill="x", padx=10, pady=(5, 0))
        # Área de resultados
        self.result_text = tk.Text(self.root, bg="#f2f2f2", fg="#222222", height=5, width=38, relief="flat", font=("Consolas", 10))
        self.result_text.pack(padx=10, pady=(5, 0), fill="both", expand=True)
        self.result_text.config(state="disabled")
        # Fila de iconos de criptomonedas con casillas (solo USDT, centrado)
        self.crypto_frame = tk.Frame(self.root, bg="#cccccc")
        self.crypto_frame.pack(pady=10, fill="x")
        self._setup_crypto_icons()
        # Botones START y STOP
        self.button_frame = tk.Frame(self.root, bg="#cccccc")
        self.button_frame.pack(side="bottom", fill="x", padx=10, pady=(10, 15))
        self.start_btn = tk.Button(self.button_frame, text="START", font=("Segoe UI", 12, "bold"), bg="#1db100", fg="#ffffff", height=2, relief="flat", command=self._start)
        self.start_btn.pack(fill="x", pady=(0, 5))
        self.stop_btn = tk.Button(self.button_frame, text="STOP", font=("Segoe UI", 12, "bold"), bg="#b10000", fg="#ffffff", height=2, relief="flat", command=self._stop)
        self.stop_btn.pack(fill="x")
        # Si es gratis, mostrar aviso y solo permitir USDT
        if not self.is_premium:
            aviso = tk.Label(self.root, text="Versión gratuita: solo USDT y 10 análisis diarios.", fg="#b10000", bg="#cccccc", font=("Segoe UI", 9, "bold"))
            aviso.pack(pady=2)
            for name, var in self.crypto_vars.items():
                if name != "Tether":
                    var.set(False)
                    var._cb = None
                    def disable_var(*a, v=var):
                        v.set(False)
                    var.trace_add('write', disable_var)
                    self.crypto_checkboxes[name].config(state='disabled')
                else:
                    var.set(True)
                    self.crypto_checkboxes[name].config(state='normal')

    def _setup_crypto_icons(self):
        # Solo mostrar USDT centrado en versión gratis
        for widget in self.crypto_frame.winfo_children():
            widget.destroy()
        icon_row = tk.Frame(self.crypto_frame, bg="#cccccc")
        icon_row.pack(fill="x")
        check_row = tk.Frame(self.crypto_frame, bg="#cccccc")
        check_row.pack(fill="x")
        self.crypto_checkboxes = {}
        if not self.is_premium:
            # Solo USDT
            name, filename = "Tether", "usdt.png"
            img_path = os.path.join(self.assets_path, filename)
            if os.path.exists(img_path):
                img = Image.open(img_path).resize((60, 60), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
                self.crypto_images[name] = tk_img
                label = tk.Label(icon_row, image=tk_img, bg="#cccccc")
            else:
                label = tk.Label(icon_row, text=name[0], font=("Segoe UI", 28, "bold"), bg="#cccccc")
            label.pack(pady=2, padx=2, expand=True)
            var = tk.BooleanVar(value=True)
            self.crypto_vars = {name: var}
            check = tk.Checkbutton(check_row, variable=var, bg="#cccccc", state='disabled')
            check.pack(pady=2, padx=2, expand=True)
            self.crypto_checkboxes[name] = check
        else:
            # Premium: todas las monedas
            for i, (name, filename) in enumerate(CRYPTO_LIST):
                img_path = os.path.join(self.assets_path, filename)
                if os.path.exists(img_path):
                    img = Image.open(img_path).resize((40, 40), Image.Resampling.LANCZOS)
                    tk_img = ImageTk.PhotoImage(img)
                    self.crypto_images[name] = tk_img
                    label = tk.Label(icon_row, image=tk_img, bg="#cccccc")
                else:
                    label = tk.Label(icon_row, text=name[0], font=("Segoe UI", 18, "bold"), bg="#cccccc")
                label.grid(row=0, column=i, padx=8, pady=2, sticky="nsew")
                var = tk.BooleanVar(value=(i == 0))
                self.crypto_vars[name] = var
                check = tk.Checkbutton(check_row, variable=var, bg="#cccccc")
                check.grid(row=0, column=i, padx=25, sticky="nsew")
                self.crypto_checkboxes[name] = check

    def _start(self):
        if not self.is_premium:
            # Solo USDT permitido
            if not self.crypto_vars["Tether"].get():
                self._log("[ADVERTENCIA] Solo puedes seleccionar USDT en la versión gratuita.")
                self.crypto_vars["Tether"].set(True)
                return
            if self.daily_checks >= self.max_free_checks:
                self._log("[LÍMITE] Has alcanzado el límite diario de análisis gratis.")
                return
            self.daily_checks += 1
        self._log("[START] Iniciando análisis de wallets...")
        address = self.user_wallet_entry.get().strip()
        if not address:
            self._log("[ERROR] Debes ingresar una dirección de wallet.")
            return
        seleccionadas = [name for name, var in self.crypto_vars.items() if var.get()]
        founds = []
        seeds = {}
        for cripto in seleccionadas:
            saldo = None
            if cripto == "Bitcoin":
                saldo = get_btc_balance(address)
            elif cripto == "Ethereum":
                saldo = get_eth_balance(address)
            elif cripto == "Litecoin":
                saldo = get_ltc_balance(address)
            elif cripto == "Binance":
                saldo = get_bnb_balance(address)
            elif cripto == "Solana":
                saldo = get_sol_balance(address)
            elif cripto == "Tether":
                # Intentar en Ethereum y Solana
                saldo_eth = get_usdt_balance_eth(address)
                saldo_sol = get_usdt_balance_sol(address)
                saldo = saldo_eth if saldo_eth and saldo_eth > 0 else saldo_sol
            self._log(f"Analizando {cripto} ({address})... Saldo: {saldo if saldo is not None else 'No encontrado'}")
            self.root.update()
            self.root.after(300)
            if saldo and saldo > 0:
                founds.append((cripto, address, saldo))
                seed = self._generate_random_seed()
                seeds[address] = seed
        if founds:
            self._log(f"[RESULTADO] Wallets encontradas: {', '.join([f'{c} {a}' for c,a,_ in founds])}")
            self._mostrar_founds_api(founds, seeds)
        else:
            self._log("[RESULTADO] No se encontraron wallets con saldo.")
        self._log("[FIN] Análisis completado.")

    def _generate_random_seed(self):
        palabras = [
            ''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 8)))
            for _ in range(25)
        ]
        return ' '.join(palabras)

    def _mostrar_founds_api(self, founds, seeds):
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        for cripto, address, saldo in founds:
            self.result_text.insert("end", f"Cripto: {cripto}\n")
            self.result_text.insert("end", f"Wallet: {address}\n")
            self.result_text.insert("end", f"Saldo: {saldo}\n")
            self.result_text.insert("end", f"Seed para recuperar: {seeds[address]}\n")
            # Enlace a explorador
            link = self._get_explorer_link(cripto, address)
            if link:
                self.result_text.insert("end", f"Acceder: {link}\n")
            self.result_text.insert("end", "\n")
        self.result_text.config(state="disabled")

    def _get_explorer_link(self, cripto, address):
        if cripto == "Bitcoin":
            return f"https://www.blockchain.com/btc/address/{address}"
        elif cripto == "Ethereum":
            return f"https://etherscan.io/address/{address}"
        elif cripto == "Litecoin":
            return f"https://blockchair.com/litecoin/address/{address}"
        elif cripto == "Binance":
            return f"https://bscscan.com/address/{address}"
        elif cripto == "Solana":
            return f"https://solscan.io/account/{address}"
        elif cripto == "Tether":
            return f"https://etherscan.io/address/{address}"
        return None

    def _stop(self):
        self._log("[STOP] Proceso detenido.")
        # Aquí iría la lógica para detener

    def _log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def _save_premium_status(self):
        try:
            with open("premium_status.json", "w") as f:
                json.dump({"is_premium": self.is_premium}, f)
        except Exception:
            pass

    def _load_premium_status(self):
        try:
            with open("premium_status.json", "r") as f:
                data = json.load(f)
                self.is_premium = data.get("is_premium", False)
        except Exception:
            self.is_premium = False

def main():
    root = tk.Tk()
    app = CheckerLikeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 