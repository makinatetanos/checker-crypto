import requests

def obtener_datos_blockchain():
    url = "https://blockchain.info/rawaddr/<wallet_address>"  # Reemplaza con la URL correcta
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        return "Conexión exitosa a la API."
    except requests.exceptions.RequestException as e:
        return f"Error al conectar con la API: {e}"