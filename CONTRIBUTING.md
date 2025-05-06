# Guía de Contribución

¡Gracias por tu interés en contribuir a Checker Crypto!

## Requisitos antes de contribuir

- Usa Python 3.9+.
- Instala las dependencias con:
  ```bash
  pip install -r requirements-dev.txt
  ```
- Asegúrate de que todos los tests pasan antes de enviar un PR:
  ```bash
  python -m pytest
  ```
- Usa type hints y sigue el estilo de código existente.
- No subas archivos de entorno, secretos ni pycache.

## Flujo de trabajo recomendado

1. Haz un fork del repositorio y crea una rama desde `main`.
2. Realiza tus cambios y añade tests que cubran tu funcionalidad.
3. Ejecuta los tests y revisa la cobertura localmente.
4. Envía un Pull Request con una descripción clara de tu cambio.

## Buenas prácticas

- Añade o actualiza documentación si tu PR introduce cambios relevantes.
- Si tu cambio es mayor, abre primero un Issue para discutirlo.
- Usa mensajes de commit descriptivos y en inglés.
- Si tu cambio es un bugfix, añade un test que lo demuestre.

¡Esperamos tus contribuciones!
