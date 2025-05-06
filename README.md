# 🔍 Monero Wallet Scanner: Encuentra tus Billeteras Perdidas de Monero de Forma Segura y Eficiente

[](https://www.google.com/search?q=URL_DE_TU_CAPTURA_DE_PANTALLA)

Este es un escáner avanzado de billeteras Monero con una interfaz gráfica intuitiva, diseñado para ayudarte a **descubrir billeteras de Monero perdidas u olvidadas** de manera segura y eficiente.

## ✨ Características Principales

  * **🖥️ Interfaz Gráfica Moderna y Personalizable:**
      * 🎨 Temas visuales claro y oscuro para adaptarse a tus preferencias.
      * 📊 Estadísticas de escaneo mostradas en tiempo real.
      * ⏳ Barra de progreso interactiva para visualizar el avance.
      * 💬 Mensajes de estado detallados para mantenerte informado.
  * **🚀 Escaneo Avanzado y Configurable:**
      * ⚙️ Escaneo asíncrono multi-hilo para un rendimiento superior.
      * ✅ Validación robusta de direcciones Monero para evitar errores.
      * 🧪 Modo de prueba integrado para facilitar el desarrollo y las pruebas.
      * 🔢 Límites configurables para el número de intentos de escaneo.
  * **🛡️ Seguridad Robusta:**
      * 🔒 Encriptación de datos sensibles para proteger tu información.
      * 🔑 Almacenamiento seguro de la información de las billeteras.
      * 🔍 Validación exhaustiva de direcciones para mayor seguridad.
      * 🛡️ Protección contra posibles inyecciones de datos.
  * **⚡ Rendimiento Optimizado:**
      * 🧠 Gestión eficiente de la memoria para un funcionamiento fluido.
      * 💾 Mecanismo de caché para acelerar la repetición de escaneos.
      * Resource Manejo eficiente de los recursos del sistema.
      * Parallel Escaneo paralelo para reducir significativamente el tiempo de búsqueda.

## ⚙️ Requisitos del Sistema

Asegúrate de tener instaladas las siguientes dependencias antes de comenzar:

  * 🐍 **Python:** Versión 3.8 o superior ([Descargar Python](https://www.python.org/downloads/))
  * 🖼️ **PyQt6:** Versión 6.6.1 o superior (`pip install PyQt6>=6.6.1`)
  * 🌐 **requests:** Versión 2.31.0 o superior (`pip install requests>=2.31.0`)
  * 🔑 **cryptography:** Versión 42.0.2 o superior (`pip install cryptography>=42.0.2`)
  * ⚙️ **python-dotenv:** Versión 1.0.1 o superior (`pip install python-dotenv>=1.0.1`)
  * 🔗 **aiohttp:** Versión 3.9.3 o superior (`pip install aiohttp>=3.9.3`)
  * ⏱️ **asyncio:** Versión 3.4.3 o superior (generalmente incluido con Python 3.7+)

## 🛠️ Guía de Instalación

Sigue estos sencillos pasos para configurar el escáner en tu sistema:

1.  **Crea un entorno virtual aislado:**

    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/macOS
    python -m venv venv
    source venv/bin/activate
    ```

2.  **Instala todas las dependencias necesarias:**

    ```bash
    pip install -r requisitos.txt
    ```

3.  **Configura tu entorno:**

      * Duplica el archivo `.env.example` y renómbralo a `.env`.
      * Abre el archivo `.env` con un editor de texto y ajusta las configuraciones según tus necesidades.

    <!-- end list -->

    ```
    MONERO_RPC_HOST=servidor_local
    MONERO_RPC_PORT=18081
    MODO_PRUEBA=verdadero
    MAX_THREADS=4
    SCAN_INTERVAL_MS=1000
    MAX_INTEMPTS=1000
    ENCRYPTION_KEY=tu_clave_secreta
    DATA_DIR=datos
    LOG_DIR=registros
    ```

-----

## 🚀 Inicio Rápido

Para ejecutar el escáner de billeteras Monero, simplemente ejecuta el siguiente comando desde la raíz del proyecto:

```bash
python -m src.verificador_monero.main
```

Esto iniciará la interfaz gráfica donde podrás configurar y comenzar el escaneo.

-----

## 🧪 Pruebas Automatizadas

El proyecto incluye un conjunto completo de pruebas para garantizar su estabilidad y correcto funcionamiento:

  * **Ejecutar todas las pruebas:**

    ```bash
    python -m pytest tests --maxfail=5 --disable-warnings -v
    ```

  * **Ejecutar solo las pruebas de integración:**

    ```bash
    python -m pytest tests/test_integration.py -v
    ```

  * **Ejecutar solo las pruebas de la interfaz gráfica (PyQt6):**

    ```bash
    python -m pytest tests/test_gui_interaction.py -v
    ```

> **⚠️ Nota Importante sobre las Pruebas de GUI en Windows:**
>
> Las pruebas de interfaz gráfica automatizadas pueden experimentar inestabilidad en sistemas Windows debido a ciertas limitaciones inherentes en la interacción entre PyQt6 y `pytest-qt`. Por esta razón, estas pruebas están marcadas intencionalmente como `xfail` (fallo esperado) para evitar que interrumpan el flujo de trabajo de desarrollo. Si observas fallos o errores de memoria durante la ejecución de las pruebas de interacción de botones en Windows, esto se considera un comportamiento esperado.
>
> La funcionalidad visual y la lógica de la interfaz de usuario pueden verificarse de manera confiable ejecutando la aplicación directamente y realizando pruebas manuales.

### 💡 Consejos para Pruebas Manuales

  * Inicia la aplicación y explora todos los botones y elementos de la interfaz para asegurar su correcta funcionalidad.
  * Verifica que los resultados del escaneo y cualquier mensaje de error se muestren de forma clara y precisa.

### 📂 Estructura del Directorio de Pruebas

  * `tests/test_monero_handler.py`: Contiene las pruebas unitarias para la lógica principal del escáner.
  * `tests/test_integration.py`: Incluye pruebas de integración que verifican el flujo completo del proceso de escaneo de billeteras.
  * `tests/test_gui_interaction.py`: Alberga las pruebas automatizadas diseñadas para interactuar con los elementos de la interfaz gráfica.
  * `tests/`: Otros archivos dentro de este directorio contienen pruebas para utilidades, configuración y la lógica relacionada con las billeteras.

## 🤝 Contribuciones

¡Tu ayuda es bienvenida\! Si tienes ideas para mejorar el escáner, encuentras algún error o quieres añadir nuevas funcionalidades, por favor:

1.  Abre un **nuevo "Issue"** en el repositorio de GitHub para discutir tu sugerencia o el problema encontrado.
2.  Si tienes una solución o mejora implementada, envía un **"Pull Request"** con tus cambios.

¡Agradecemos tu colaboración\!

## ⚙️ Opciones de Configuración (`.env`)

El archivo `.env` te permite personalizar el comportamiento del escáner. Aquí tienes una descripción de las variables disponibles:

| Variable            | Descripción                                  | Valor por defecto |
| :------------------ | :------------------------------------------- | :---------------- |
| `MONERO_RPC_HOST`   | Dirección del host del nodo RPC de Monero. | `servidor_local`  |
| `MONERO_RPC_PORT`   | Puerto de comunicación del nodo RPC.       | `18081`           |
| `MODO_PRUEBA`       | Activa el modo de prueba para desarrollo.    | `verdadero`       |
| `MAX_THREADS`       | Número máximo de hilos para el escaneo.      | `4`               |
| `SCAN_INTERVAL_MS`  | Intervalo en milisegundos entre intentos.   | `1000`            |
| `MAX_INTEMPTS`      | Número máximo de intentos de escaneo.       | `1000`            |
| `ENCRYPTION_KEY`    | Clave para encriptar datos sensibles.        | `-`               |
| `DATA_DIR`          | Directorio para almacenar datos.             | `datos`           |
| `LOG_DIR`           | Directorio para guardar los archivos de registro. | `registros`       |

## 📝 Licencia

Este software es **privado y propietario**. Todos los derechos están reservados. Queda estrictamente prohibida cualquier copia, distribución, modificación o uso no autorizado sin el consentimiento explícito y por escrito del titular de los derechos de autor. No se concede ninguna licencia de uso, redistribución o acceso al código fuente a menos que se otorgue una autorización expresa.

## ⚠️ Aviso Legal

Este software se proporciona **únicamente con fines educativos**. El uso de este software para cualquier actividad que pueda ser considerada ilegal está **estrictamente prohibido**. Los desarrolladores de este software no asumen ninguna responsabilidad por cualquier uso indebido o ilegal que se le pueda dar.

## 📞 Soporte

Si encuentras algún problema durante el uso del escáner o tienes alguna sugerencia para mejorarlo, por favor, sigue estos pasos para contactar al equipo de soporte:

1.  **Abre un nuevo "Issue"** en el repositorio de GitHub.
2.  **Describe detalladamente el problema** que has encontrado o la sugerencia que quieres hacer.
3.  **Incluye los pasos necesarios para reproducir el problema** (si aplica).
4.  **Adjunta cualquier archivo de registro (logs) o capturas de pantalla** que puedan ser útiles para entender mejor la situación (si aplica).

# 🏷️ Etiquetas para SEO en GitHub

```
#monero #wallet #scanner #billetera #recuperar #perdida #abandonada #seguridad #privacidad #criptomoneda #herramienta #utilidad #python #gui #pyqt #escaneo #asincrono #multi-hilo #busqueda
```
