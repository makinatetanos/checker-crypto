import tkinter as tk
from tkinter import messagebox
from src.blockchain_api import obtener_datos_blockchain
from src.wallet_analyzer import analizar_wallets

def conectar_api():
    resultado = obtener_datos_blockchain()
    messagebox.showinfo("Conexión a la API", resultado)

def analizar():
    resultado = analizar_wallets()
    messagebox.showinfo("Análisis de Wallets", resultado)

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Checker Crypto")
ventana.geometry("400x300")

# Botones
btn_conectar = tk.Button(ventana, text="Conectar a la API", command=conectar_api)
btn_conectar.pack(pady=10)

btn_analizar = tk.Button(ventana, text="Analizar Wallets", command=analizar)
btn_analizar.pack(pady=10)

# Iniciar el bucle principal
ventana.mainloop()