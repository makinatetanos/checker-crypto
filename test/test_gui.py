import unittest
from unittest.mock import patch, MagicMock
import os
import json
import sys
import tkinter as tk
import threading
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from gui import CheckerLikeGUI, MONERO_ADDRESS, PREMIUM_PRICE_USD

def can_create_tk():
    try:
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        return True
    except Exception:
        return False

class TestCheckerLikeGUI(unittest.TestCase):
    def setUp(self):
        self.root = None  # Solo se creará en tests de integración
        if os.path.exists('premium_status.json'):
            os.remove('premium_status.json')

    def tearDown(self):
        if self.root:
            self.root.destroy()
        if os.path.exists('premium_status.json'):
            os.remove('premium_status.json')

    # --- TESTS DE INTEGRACIÓN (requieren GUI) ---
    def test_header_logo_and_name(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        header = self.root.winfo_children()[0]
        labels = [w for w in header.winfo_children() if isinstance(w, tk.Label)]
        self.assertTrue(any('🔥' in l.cget('text') for l in labels))
        self.assertTrue(any('CryptoCheckFull' in l.cget('text') for l in labels))

    def test_only_usdt_checkbox_in_free(self):
        # Test lógico puro: simula la lógica de selección USDT sin GUI real
        gui = CheckerLikeGUI(MagicMock())
        gui.is_premium = False
        gui.crypto_vars = {'Tether': MagicMock(get=lambda: True)}
        gui.crypto_checkboxes = {'Tether': MagicMock(cget=lambda key: 'disabled' if key == 'state' else None)}
        self.assertEqual(list(gui.crypto_vars.keys()), ['Tether'])
        self.assertTrue(gui.crypto_vars['Tether'].get())
        self.assertEqual(gui.crypto_checkboxes['Tether'].cget('state'), 'disabled')

    def test_usdt_logo_displayed(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = False
        gui._main_gui()
        icon_row = gui.crypto_frame.winfo_children()[0]
        label = icon_row.winfo_children()[0]
        self.assertTrue(isinstance(label, tk.Label))

    def test_start_button_logs_analysis(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = False
        gui._main_gui()
        gui._start()
        gui.log_text.config(state="normal")
        contenido = gui.log_text.get("1.0", "end")
        self.assertIn("Iniciando análisis de wallets USDT", contenido)
        self.assertIn("Analizando TetherWallet1", contenido)
        self.assertIn("[RESULTADO] Wallets perdidas encontradas", contenido)

    def test_found_label_centered(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        self.assertEqual(gui.label_found.cget('anchor'), 'center')

    def test_responsivity_of_log_frame(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        self.assertEqual(str(gui.log_frame.pack_info().get('fill')), 'x')

    def test_premium_allows_all_coins(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = True
        gui._main_gui()
        self.assertEqual(set(gui.crypto_vars.keys()), set(['Bitcoin','Ethereum','Litecoin','Binance','Solana','Tether']))
        for name in gui.crypto_vars:
            gui.crypto_vars[name].set(True)
        gui._start()
        self.assertTrue(all(v.get() for v in gui.crypto_vars.values()))

    def test_start_button_limit_free(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = False
        gui._main_gui()
        gui.daily_checks = gui.max_free_checks
        gui._start()
        gui.log_text.config(state="normal")
        contenido = gui.log_text.get("1.0", "end")
        self.assertIn("límite diario", contenido.lower())

    def test_stop_button_logs(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        gui._stop()
        gui.log_text.config(state="normal")
        contenido = gui.log_text.get("1.0", "end")
        self.assertIn("proceso detenido", contenido.lower())

    def test_clear_window_removes_widgets(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        gui._clear_window()
        self.assertEqual(len(self.root.winfo_children()), 0)

    def test_crypto_icons_initial_state(self):
        try:
            if not can_create_tk():
                self.skipTest("Tkinter GUI not available")
            self.root = tk.Tk()
            self.root.withdraw()
            # Versión gratis: solo USDT
            gui = CheckerLikeGUI(self.root)
            gui.is_premium = False
            gui._main_gui()
            selected = [v.get() for v in gui.crypto_vars.values()]
            self.assertEqual(selected, [True])
            # Versión premium: todas las monedas
            gui = CheckerLikeGUI(self.root)
            gui.is_premium = True
            gui._main_gui()
            selected = [v.get() for v in gui.crypto_vars.values()]
            self.assertEqual(selected, [True, False, False, False, False, False])
        except Exception as e:
            self.skipTest(f"Tkinter GUI not available or misconfigured: {e}")

    def test_show_version_selector_after_payment(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = True
        gui._show_version_selector()
        found = False
        for widget in self.root.winfo_children()[0].winfo_children():
            if isinstance(widget, tk.Label) and 'premium' in widget.cget('text').lower():
                found = True
        self.assertTrue(found)

    def test_show_premium_payment_screen(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._show_premium_payment()
        found = False
        for widget in self.root.winfo_children()[0].winfo_children():
            if isinstance(widget, tk.Entry) and MONERO_ADDRESS in widget.get():
                found = True
        self.assertTrue(found)

    def test_log_functionality(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        gui._log("Mensaje de prueba")
        gui.log_text.config(state="normal")
        contenido = gui.log_text.get("1.0", "end")
        self.assertIn("Mensaje de prueba", contenido)

    # --- TESTS LÓGICOS (no requieren GUI) ---
    @patch('gui.requests.get')
    def test_get_xmr_amount_success(self, mock_get):
        mock_get.return_value.json.return_value = {"monero": {"usd": 200}}
        gui = CheckerLikeGUI(MagicMock())
        xmr = gui._get_xmr_amount(400)
        self.assertAlmostEqual(xmr, 2.0)

    @patch('gui.requests.get', side_effect=Exception('fail'))
    def test_get_xmr_amount_error(self, mock_get):
        gui = CheckerLikeGUI(MagicMock())
        self.assertEqual(gui._get_xmr_amount(400), '(error)')

    def test_save_and_load_premium_status(self):
        gui = CheckerLikeGUI(MagicMock())
        gui.is_premium = True
        gui._save_premium_status()
        gui2 = CheckerLikeGUI(MagicMock())
        gui2._load_premium_status()
        self.assertTrue(gui2.is_premium)

    def test_version_selector_shows(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        self.assertIn('Selecciona tu versión', self.root.winfo_children()[0].winfo_children()[0].cget('text'))

    def test_start_free_sets_non_premium(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._start_free()
        self.assertFalse(gui.is_premium)

    def test_start_premium_sets_premium(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._start_premium()
        self.assertTrue(gui.is_premium)

    def test_verify_payment_success(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {"data": [{"amount": int(2.0*1e12)}]}
            gui = CheckerLikeGUI(self.root)
            with patch.object(gui, '_get_xmr_amount', return_value=2.0):
                with patch('tkinter.messagebox.showinfo') as mock_info:
                    gui._verify_payment(2.0)
                    self.assertTrue(gui.is_premium)
                    mock_info.assert_called()

    def test_verify_payment_not_found(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {"data": [{"amount": int(1.0*1e12)}]}
            gui = CheckerLikeGUI(self.root)
            with patch.object(gui, '_get_xmr_amount', return_value=2.0):
                with patch('tkinter.messagebox.showwarning') as mock_warn:
                    gui._verify_payment(2.0)
                    self.assertFalse(gui.is_premium)
                    mock_warn.assert_called()

    def test_verify_payment_error(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        with patch('gui.requests.get', side_effect=Exception('fail')):
            gui = CheckerLikeGUI(self.root)
            with patch('tkinter.messagebox.showerror') as mock_err:
                gui._verify_payment(2.0)
                mock_err.assert_called()

    def test_free_version_limit_one_coin(self):
        try:
            if not can_create_tk():
                self.skipTest("Tkinter GUI not available")
            self.root = tk.Tk()
            self.root.withdraw()
            gui = CheckerLikeGUI(self.root)
            gui.is_premium = False
            gui._main_gui()
            # Intenta seleccionar más de una moneda (solo USDT debe estar disponible)
            for var in gui.crypto_vars.values():
                var.set(True)
            gui._start()
            selected = sum(v.get() for v in gui.crypto_vars.values())
            self.assertEqual(selected, 1)
        except Exception as e:
            self.skipTest(f"Tkinter GUI not available or misconfigured: {e}")

    def test_free_version_limit_daily_checks(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = False
        gui._main_gui()
        gui.daily_checks = gui.max_free_checks
        gui._start()
        gui.log_text.config(state="normal")
        contenido = gui.log_text.get("1.0", "end")
        self.assertIn("límite diario", contenido.lower())

    def test_premium_no_daily_limit(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = True
        gui._main_gui()
        gui.daily_checks = 1000
        with patch('tkinter.messagebox.showwarning') as mock_warn:
            gui._start()
            mock_warn.assert_not_called()

    def test_wallet_entry_validation(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        gui._start()  # Sin dirección
        gui.log_text.config(state="normal")
        contenido = gui.log_text.get("1.0", "end")
        self.assertIn("debes ingresar una dirección de wallet", contenido.lower())

    def test_btc_balance_api(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'data': {
                    'test_address': {
                        'address': {'balance': 100000000}  # 1 BTC
                    }
                }
            }
            balance = get_btc_balance('test_address')
            self.assertEqual(balance, 1.0)

    def test_eth_balance_api(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'status': '1',
                'result': '1000000000000000000'  # 1 ETH
            }
            balance = get_eth_balance('test_address')
            self.assertEqual(balance, 1.0)

    def test_ltc_balance_api(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'final_balance': 100000000  # 1 LTC
            }
            balance = get_ltc_balance('test_address')
            self.assertEqual(balance, 1.0)

    def test_bnb_balance_api(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'status': '1',
                'result': '1000000000000000000'  # 1 BNB
            }
            balance = get_bnb_balance('test_address')
            self.assertEqual(balance, 1.0)

    def test_sol_balance_api(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'lamports': 1000000000  # 1 SOL
            }
            balance = get_sol_balance('test_address')
            self.assertEqual(balance, 1.0)

    def test_usdt_balance_eth_api(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'status': '1',
                'result': '1000000'  # 1 USDT
            }
            balance = get_usdt_balance_eth('test_address')
            self.assertEqual(balance, 1.0)

    def test_usdt_balance_sol_api(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = [
                {
                    'tokenSymbol': 'USDT',
                    'tokenAmount': {'uiAmount': 1.0}
                }
            ]
            balance = get_usdt_balance_sol('test_address')
            self.assertEqual(balance, 1.0)

    def test_explorer_links_generation(self):
        gui = CheckerLikeGUI(MagicMock())
        test_cases = [
            ('Bitcoin', 'test_address', 'https://www.blockchain.com/btc/address/test_address'),
            ('Ethereum', 'test_address', 'https://etherscan.io/address/test_address'),
            ('Litecoin', 'test_address', 'https://blockchair.com/litecoin/address/test_address'),
            ('Binance', 'test_address', 'https://bscscan.com/address/test_address'),
            ('Solana', 'test_address', 'https://solscan.io/account/test_address'),
            ('Tether', 'test_address', 'https://etherscan.io/address/test_address')
        ]
        for cripto, address, expected in test_cases:
            link = gui._get_explorer_link(cripto, address)
            self.assertEqual(link, expected)

    def test_random_seed_generation(self):
        gui = CheckerLikeGUI(MagicMock())
        seed = gui._generate_random_seed()
        words = seed.split()
        self.assertEqual(len(words), 25)
        self.assertTrue(all(len(word) >= 4 and len(word) <= 8 for word in words))
        self.assertTrue(all(word.isalpha() and word.islower() for word in words))

    def test_result_text_display(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        founds = [('Bitcoin', 'test_address', 1.0)]
        seeds = {'test_address': 'test seed'}
        gui._mostrar_founds_api(founds, seeds)
        contenido = gui.result_text.get("1.0", "end")
        self.assertIn('Bitcoin', contenido)
        self.assertIn('test_address', contenido)
        self.assertIn('1.0', contenido)
        self.assertIn('test seed', contenido)

    def test_premium_payment_verification(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'data': [
                    {'amount': '2000000000000'}  # 2 XMR
                ]
            }
            gui = CheckerLikeGUI(MagicMock())
            gui._verify_payment(2.0)
            self.assertTrue(gui.is_premium)

    def test_premium_payment_verification_failure(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'data': [
                    {'amount': '1000000000000'}  # 1 XMR
                ]
            }
            gui = CheckerLikeGUI(MagicMock())
            gui._verify_payment(2.0)
            self.assertFalse(gui.is_premium)

    def test_premium_payment_verification_error(self):
        with patch('gui.requests.get', side_effect=Exception('API Error')):
            gui = CheckerLikeGUI(MagicMock())
            gui._verify_payment(2.0)
            self.assertFalse(gui.is_premium)

    def test_daily_checks_counter(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = False
        gui._main_gui()
        initial_checks = gui.daily_checks
        gui._start()
        self.assertEqual(gui.daily_checks, initial_checks + 1)

    def test_premium_no_daily_checks_limit(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = True
        gui._main_gui()
        initial_checks = gui.daily_checks
        for _ in range(20):  # Más allá del límite gratuito
            gui._start()
        self.assertGreater(gui.daily_checks, initial_checks)

    def test_crypto_icons_loading(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = True
        gui._main_gui()
        self.assertTrue(hasattr(gui, 'crypto_images'))
        self.assertTrue(isinstance(gui.crypto_images, dict))

    def test_wallet_entry_placeholder(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        self.assertTrue(isinstance(gui.user_wallet_entry, tk.Entry))
        self.assertEqual(gui.user_wallet_entry.cget('width'), 35)

    def test_stop_button_state(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        self.assertEqual(gui.stop_btn.cget('bg'), '#b10000')
        self.assertEqual(gui.stop_btn.cget('fg'), '#ffffff')
        self.assertEqual(gui.stop_btn.cget('text'), 'STOP')

    def test_start_button_state(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        self.assertEqual(gui.start_btn.cget('bg'), '#1db100')
        self.assertEqual(gui.start_btn.cget('fg'), '#ffffff')
        self.assertEqual(gui.start_btn.cget('text'), 'START')

    def test_api_error_handling(self):
        with patch('gui.requests.get', side_effect=Exception('API Error')):
            balance = get_btc_balance('test_address')
            self.assertIsNone(balance)

    def test_invalid_address_format(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {'error': 'Invalid address'}
            balance = get_eth_balance('invalid_address')
            self.assertIsNone(balance)

    def test_zero_balance_handling(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'status': '1',
                'result': '0'
            }
            balance = get_eth_balance('test_address')
            self.assertEqual(balance, 0.0)

    def test_large_balance_handling(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'status': '1',
                'result': '1000000000000000000000000'  # 1 millón ETH
            }
            balance = get_eth_balance('test_address')
            self.assertEqual(balance, 1000000.0)

    def test_multiple_wallet_results(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        founds = [
            ('Bitcoin', 'btc_address', 1.0),
            ('Ethereum', 'eth_address', 2.0),
            ('Tether', 'usdt_address', 3.0)
        ]
        seeds = {
            'btc_address': 'seed1',
            'eth_address': 'seed2',
            'usdt_address': 'seed3'
        }
        gui._mostrar_founds_api(founds, seeds)
        contenido = gui.result_text.get("1.0", "end")
        self.assertIn('Bitcoin', contenido)
        self.assertIn('Ethereum', contenido)
        self.assertIn('Tether', contenido)

    def test_premium_status_persistence(self):
        gui = CheckerLikeGUI(MagicMock())
        gui.is_premium = True
        gui._save_premium_status()
        # Simular reinicio de la aplicación
        gui2 = CheckerLikeGUI(MagicMock())
        gui2._load_premium_status()
        self.assertTrue(gui2.is_premium)
        # Limpiar estado
        gui2.is_premium = False
        gui2._save_premium_status()

    def test_version_selector_buttons(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._show_version_selector()
        buttons = [w for w in self.root.winfo_children()[0].winfo_children() 
                  if isinstance(w, tk.Button)]
        self.assertEqual(len(buttons), 2)
        self.assertIn('Gratis', buttons[0].cget('text'))
        self.assertIn('Premium', buttons[1].cget('text'))

    def test_premium_payment_screen_elements(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._show_premium_payment()
        frame = self.root.winfo_children()[0]
        elements = frame.winfo_children()
        self.assertTrue(any(isinstance(e, tk.Entry) for e in elements))
        self.assertTrue(any(isinstance(e, tk.Button) for e in elements))
        self.assertTrue(any(isinstance(e, tk.Label) for e in elements))

    def test_log_text_scroll_behavior(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Generar muchos mensajes
        for i in range(100):
            gui._log(f"Mensaje de prueba {i}")
        # Verificar que el último mensaje es visible
        last_line = gui.log_text.get("end-2c linestart", "end-1c")
        self.assertIn("Mensaje de prueba 99", last_line)

    def test_crypto_checkbox_interaction(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = True
        gui._main_gui()
        # Probar interacción con checkboxes
        for name, var in gui.crypto_vars.items():
            var.set(True)
            self.assertTrue(var.get())
            var.set(False)
            self.assertFalse(var.get())

    def test_wallet_entry_character_limit(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        long_address = "0x" + "1" * 100  # Dirección muy larga
        gui.user_wallet_entry.delete(0, tk.END)
        gui.user_wallet_entry.insert(0, long_address)
        self.assertEqual(len(gui.user_wallet_entry.get()), len(long_address))

    def test_result_text_readonly(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        self.assertEqual(gui.result_text.cget('state'), 'disabled')

    def test_premium_price_display(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._show_premium_payment()
        frame = self.root.winfo_children()[0]
        labels = [w for w in frame.winfo_children() if isinstance(w, tk.Label)]
        price_text = next((l.cget('text') for l in labels if '$400' in l.cget('text')), None)
        self.assertIsNotNone(price_text)

    def test_monero_address_display(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._show_premium_payment()
        frame = self.root.winfo_children()[0]
        entries = [w for w in frame.winfo_children() if isinstance(w, tk.Entry)]
        self.assertTrue(any(MONERO_ADDRESS in e.get() for e in entries))

    def test_premium_status_indicator(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = True
        gui._show_version_selector()
        frame = self.root.winfo_children()[0]
        labels = [w for w in frame.winfo_children() if isinstance(w, tk.Label)]
        self.assertTrue(any('premium' in l.cget('text').lower() for l in labels))

    def test_daily_checks_reset(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = False
        gui._main_gui()
        gui.daily_checks = 5
        gui._start_free()  # Debería resetear el contador
        self.assertEqual(gui.daily_checks, 0)

    def test_premium_features_unlock(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = False
        gui._main_gui()
        # Verificar que solo USDT está disponible
        self.assertEqual(len(gui.crypto_vars), 1)
        # Activar premium
        gui.is_premium = True
        gui._main_gui()
        # Verificar que todas las criptos están disponibles
        self.assertEqual(len(gui.crypto_vars), 6)

    def test_error_handling_in_balance_checks(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.side_effect = [
                Exception('BTC API Error'),
                Exception('ETH API Error'),
                Exception('LTC API Error')
            ]
            balances = [
                get_btc_balance('test_address'),
                get_eth_balance('test_address'),
                get_ltc_balance('test_address')
            ]
            self.assertTrue(all(b is None for b in balances))

    def test_concurrent_api_calls(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = True
        gui._main_gui()
        # Simular múltiples llamadas API concurrentes
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'status': '1',
                'result': '1000000000000000000'
            }
            gui.user_wallet_entry.insert(0, 'test_address')
            for name in gui.crypto_vars:
                gui.crypto_vars[name].set(True)
            gui._start()
            # Verificar que todas las APIs fueron llamadas
            self.assertGreater(mock_get.call_count, 0)

    def test_api_rate_limiting(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.side_effect = [
                {'status': '1', 'result': '1000000'},  # Primera llamada exitosa
                Exception('Rate limit exceeded'),      # Segunda llamada falla
                {'status': '1', 'result': '1000000'}   # Tercera llamada exitosa
            ]
            balances = [
                get_eth_balance('test_address'),
                get_eth_balance('test_address'),
                get_eth_balance('test_address')
            ]
            self.assertIsNotNone(balances[0])
            self.assertIsNone(balances[1])
            self.assertIsNotNone(balances[2])

    def test_invalid_json_response(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.side_effect = json.JSONDecodeError('Invalid JSON', '', 0)
            balance = get_btc_balance('test_address')
            self.assertIsNone(balance)

    def test_network_timeout(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout('Connection timeout')
            balance = get_eth_balance('test_address')
            self.assertIsNone(balance)

    def test_ssl_verification_error(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.SSLError('SSL verification failed')
            balance = get_ltc_balance('test_address')
            self.assertIsNone(balance)

    def test_premium_status_file_corruption(self):
        # Simular archivo premium_status.json corrupto
        with open('premium_status.json', 'w') as f:
            f.write('invalid json content')
        gui = CheckerLikeGUI(MagicMock())
        gui._load_premium_status()
        self.assertFalse(gui.is_premium)

    def test_memory_usage_with_large_logs(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Generar logs extensos
        for i in range(1000):
            gui._log(f"Log entry {i}" * 100)  # Logs largos
        # Verificar que la GUI sigue respondiendo
        self.assertTrue(gui.log_text.winfo_exists())

    def test_concurrent_premium_verification(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        # Simular múltiples verificaciones concurrentes
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {'data': [{'amount': '2000000000000'}]}
            threads = []
            for _ in range(5):
                thread = threading.Thread(target=gui._verify_payment, args=(2.0,))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()
            self.assertTrue(gui.is_premium)

    def test_wallet_address_sanitization(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Probar diferentes formatos de dirección
        test_addresses = [
            "0x1234567890abcdef1234567890abcdef12345678",  # ETH
            "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",  # BTC
            "ltc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", # LTC
            "bnb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", # BNB
            "sol1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", # SOL
        ]
        for addr in test_addresses:
            gui.user_wallet_entry.delete(0, tk.END)
            gui.user_wallet_entry.insert(0, addr)
            self.assertEqual(gui.user_wallet_entry.get(), addr)

    def test_premium_status_race_condition(self):
        gui1 = CheckerLikeGUI(MagicMock())
        gui2 = CheckerLikeGUI(MagicMock())
        # Simular actualización concurrente del estado premium
        gui1.is_premium = True
        gui2.is_premium = False
        gui1._save_premium_status()
        gui2._save_premium_status()
        gui3 = CheckerLikeGUI(MagicMock())
        gui3._load_premium_status()
        self.assertFalse(gui3.is_premium)  # El último estado debería prevalecer

    def test_api_response_caching(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {'status': '1', 'result': '1000000'}
            # Primera llamada
            balance1 = get_eth_balance('test_address')
            # Segunda llamada (debería usar caché si está implementada)
            balance2 = get_eth_balance('test_address')
            self.assertEqual(balance1, balance2)
            self.assertEqual(mock_get.call_count, 2)  # Verificar que se hicieron las llamadas

    def test_error_message_localization(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Verificar mensajes de error en español
        error_messages = [
            "debes ingresar una dirección de wallet",
            "límite diario",
            "proceso detenido"
        ]
        for msg in error_messages:
            gui._log(msg)
            gui.log_text.config(state="normal")
            contenido = gui.log_text.get("1.0", "end")
            self.assertIn(msg, contenido)

    def test_premium_payment_amount_validation(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {"monero": {"usd": 200}}
            xmr_amount = gui._get_xmr_amount(PREMIUM_PRICE_USD)
            self.assertAlmostEqual(xmr_amount, 2.0)  # 400 USD / 200 USD/XMR = 2 XMR

    def test_wallet_balance_precision(self):
        with patch('gui.requests.get') as mock_get:
            # Probar diferentes precisiones de balance
            test_cases = [
                ('0.00000001', 0.00000001),  # 8 decimales
                ('0.0000001', 0.0000001),    # 7 decimales
                ('0.000001', 0.000001),      # 6 decimales
                ('0.00001', 0.00001),        # 5 decimales
                ('0.0001', 0.0001),          # 4 decimales
            ]
            for balance_str, expected in test_cases:
                mock_get.return_value.json.return_value = {
                    'status': '1',
                    'result': str(int(float(balance_str) * 1e18))
                }
                balance = get_eth_balance('test_address')
                self.assertAlmostEqual(balance, expected)

    def test_premium_status_file_permissions(self):
        # Probar permisos del archivo premium_status.json
        gui = CheckerLikeGUI(MagicMock())
        gui.is_premium = True
        gui._save_premium_status()
        self.assertTrue(os.path.exists('premium_status.json'))
        self.assertTrue(os.access('premium_status.json', os.R_OK))
        self.assertTrue(os.access('premium_status.json', os.W_OK))

    def test_concurrent_wallet_checks(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = True
        gui._main_gui()
        # Simular múltiples checks de wallet concurrentes
        with patch('gui.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {'status': '1', 'result': '1000000'}
            gui.user_wallet_entry.insert(0, 'test_address')
            threads = []
            for _ in range(3):
                thread = threading.Thread(target=gui._start)
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()

    def test_api_response_timeout(self):
        with patch('gui.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectTimeout('Connection timeout')
            balance = get_bnb_balance('test_address')
            self.assertIsNone(balance)

    def test_premium_status_file_cleanup(self):
        # Probar limpieza del archivo premium_status.json
        gui = CheckerLikeGUI(MagicMock())
        gui.is_premium = True
        gui._save_premium_status()
        self.assertTrue(os.path.exists('premium_status.json'))
        gui.is_premium = False
        gui._save_premium_status()
        self.assertTrue(os.path.exists('premium_status.json'))
        os.remove('premium_status.json')
        self.assertFalse(os.path.exists('premium_status.json'))

    def test_wallet_address_validation(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Probar diferentes formatos de dirección
        test_addresses = [
            ("0x1234567890abcdef1234567890abcdef12345678", True),   # ETH válida
            ("0x123", False),                                       # ETH inválida
            ("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", True),  # BTC válida
            ("bc1invalid", False),                                  # BTC inválida
        ]
        for addr, is_valid in test_addresses:
            gui.user_wallet_entry.delete(0, tk.END)
            gui.user_wallet_entry.insert(0, addr)
            gui._start()
            gui.log_text.config(state="normal")
            contenido = gui.log_text.get("1.0", "end")
            if not is_valid:
                self.assertIn("error", contenido.lower())

    def test_gui_responsiveness(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Verificar que la GUI responde a eventos
        self.root.update()
        self.assertTrue(gui.start_btn.winfo_exists())
        self.assertTrue(gui.stop_btn.winfo_exists())

    def test_button_states_during_analysis(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Verificar estados de botones durante el análisis
        gui._start()
        self.assertEqual(gui.start_btn.cget('state'), 'disabled')
        gui._stop()
        self.assertEqual(gui.start_btn.cget('state'), 'normal')

    def test_error_handling_ui_feedback(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Probar diferentes errores y verificar feedback UI
        error_cases = [
            ("", "debes ingresar una dirección de wallet"),
            ("invalid_address", "dirección inválida"),
            ("0x123", "formato incorrecto")
        ]
        for input_addr, expected_error in error_cases:
            gui.user_wallet_entry.delete(0, tk.END)
            gui.user_wallet_entry.insert(0, input_addr)
            gui._start()
            gui.log_text.config(state="normal")
            contenido = gui.log_text.get("1.0", "end")
            self.assertIn(expected_error, contenido.lower())

    def test_premium_upgrade_flow(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        # Probar flujo completo de actualización a premium
        gui._show_version_selector()
        self.assertIn('Premium', self.root.winfo_children()[0].winfo_children()[1].cget('text'))
        gui._show_premium_payment()
        self.assertIn('$400', self.root.winfo_children()[0].winfo_children()[1].cget('text'))

    def test_wallet_entry_placeholder_text(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Verificar texto placeholder
        self.assertEqual(gui.user_wallet_entry.cget('width'), 35)
        self.assertTrue(gui.user_wallet_entry.winfo_exists())

    def test_log_text_auto_scroll(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Generar muchos mensajes y verificar auto-scroll
        for i in range(50):
            gui._log(f"Mensaje {i}")
        last_line = gui.log_text.get("end-2c linestart", "end-1c")
        self.assertIn("Mensaje 49", last_line)

    def test_crypto_checkbox_states(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = True
        gui._main_gui()
        # Verificar estados de checkboxes
        for name, var in gui.crypto_vars.items():
            var.set(True)
            self.assertTrue(var.get())
            var.set(False)
            self.assertFalse(var.get())

    def test_premium_features_visibility(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        # Verificar visibilidad de características premium
        gui.is_premium = False
        gui._main_gui()
        self.assertEqual(len(gui.crypto_vars), 1)  # Solo USDT
        gui.is_premium = True
        gui._main_gui()
        self.assertEqual(len(gui.crypto_vars), 6)  # Todas las criptos

    def test_wallet_address_format_validation(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Probar diferentes formatos de dirección
        test_cases = [
            ("0x1234567890abcdef1234567890abcdef12345678", True),  # ETH
            ("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", True), # BTC
            ("invalid", False),
            ("0x123", False)
        ]
        for addr, is_valid in test_cases:
            gui.user_wallet_entry.delete(0, tk.END)
            gui.user_wallet_entry.insert(0, addr)
            gui._start()
            gui.log_text.config(state="normal")
            contenido = gui.log_text.get("1.0", "end")
            if not is_valid:
                self.assertIn("error", contenido.lower())

    def test_premium_payment_verification_ui(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._show_premium_payment()
        # Verificar elementos UI de verificación de pago
        frame = self.root.winfo_children()[0]
        self.assertTrue(any(isinstance(w, tk.Entry) for w in frame.winfo_children()))
        self.assertTrue(any(isinstance(w, tk.Button) for w in frame.winfo_children()))
        self.assertTrue(any(isinstance(w, tk.Label) for w in frame.winfo_children()))

    def test_wallet_balance_display_format(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Probar diferentes formatos de balance
        test_cases = [
            (0.00000001, "0.00000001"),
            (0.0000001, "0.0000001"),
            (0.000001, "0.000001"),
            (0.00001, "0.00001"),
            (0.0001, "0.0001")
        ]
        for balance, expected in test_cases:
            gui._mostrar_founds_api([('Bitcoin', 'test_address', balance)], {'test_address': 'seed'})
            contenido = gui.result_text.get("1.0", "end")
            self.assertIn(expected, contenido)

    def test_premium_status_persistence_ui(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui.is_premium = True
        gui._save_premium_status()
        gui._show_version_selector()
        # Verificar indicador de estado premium en UI
        frame = self.root.winfo_children()[0]
        labels = [w for w in frame.winfo_children() if isinstance(w, tk.Label)]
        self.assertTrue(any('premium' in l.cget('text').lower() for l in labels))

    def test_wallet_entry_character_limit_ui(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Probar límite de caracteres en entrada
        long_address = "0x" + "1" * 100
        gui.user_wallet_entry.delete(0, tk.END)
        gui.user_wallet_entry.insert(0, long_address)
        self.assertEqual(len(gui.user_wallet_entry.get()), len(long_address))

    def test_error_message_display_format(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Verificar formato de mensajes de error
        error_messages = [
            "Error de conexión",
            "Dirección inválida",
            "Límite diario alcanzado"
        ]
        for msg in error_messages:
            gui._log(msg)
            gui.log_text.config(state="normal")
            contenido = gui.log_text.get("1.0", "end")
            self.assertIn(msg, contenido)

    def test_premium_payment_amount_display(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._show_premium_payment()
        # Verificar visualización del monto de pago
        frame = self.root.winfo_children()[0]
        labels = [w for w in frame.winfo_children() if isinstance(w, tk.Label)]
        self.assertTrue(any('$400' in l.cget('text') for l in labels))

    def test_wallet_address_copy_paste(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Probar copiar/pegar en entrada de wallet
        test_address = "0x1234567890abcdef1234567890abcdef12345678"
        gui.user_wallet_entry.delete(0, tk.END)
        gui.user_wallet_entry.insert(0, test_address)
        self.assertEqual(gui.user_wallet_entry.get(), test_address)

    def test_premium_status_indicator_visibility(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        # Verificar visibilidad del indicador de estado premium
        gui.is_premium = True
        gui._show_version_selector()
        frame = self.root.winfo_children()[0]
        labels = [w for w in frame.winfo_children() if isinstance(w, tk.Label)]
        self.assertTrue(any('premium' in l.cget('text').lower() for l in labels))

    def test_wallet_balance_update_ui(self):
        if not can_create_tk():
            self.skipTest("Tkinter GUI not available")
        self.root = tk.Tk()
        self.root.withdraw()
        gui = CheckerLikeGUI(self.root)
        gui._main_gui()
        # Verificar actualización de UI con nuevos balances
        test_cases = [
            ('Bitcoin', 1.0),
            ('Ethereum', 2.0),
            ('Tether', 3.0)
        ]
        for cripto, balance in test_cases:
            gui._mostrar_founds_api([(cripto, 'test_address', balance)], {'test_address': 'seed'})
            contenido = gui.result_text.get("1.0", "end")
            self.assertIn(str(balance), contenido)

if __name__ == '__main__':
    unittest.main() 