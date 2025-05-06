import pytest
import requests
from unittest.mock import patch, Mock
import sys
from pathlib import Path

# Agregar el directorio src al path de Python
sys.path.append(str(Path(__file__).parent.parent))

from src.blockchain_api import obtener_datos_blockchain

def test_obtener_datos_blockchain_exitoso():
    # Simular una respuesta exitosa
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        resultado = obtener_datos_blockchain()
        assert resultado == "Conexión exitosa a la API."
        mock_get.assert_called_once()

def test_obtener_datos_blockchain_error_conexion():
    # Simular un error de conexión
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError("Error de conexión")
        
        resultado = obtener_datos_blockchain()
        assert "Error al conectar con la API" in resultado
        mock_get.assert_called_once()

def test_obtener_datos_blockchain_timeout():
    # Simular un timeout
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")
        
        resultado = obtener_datos_blockchain()
        assert "Error al conectar con la API" in resultado
        mock_get.assert_called_once()

def test_obtener_datos_blockchain_error_http():
    # Simular un error HTTP
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_get.return_value = mock_response
        
        resultado = obtener_datos_blockchain()
        assert "Error al conectar con la API" in resultado
        mock_get.assert_called_once()
