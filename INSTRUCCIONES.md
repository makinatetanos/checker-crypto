# 📦 Publicar y colaborar en Checker Crypto (Instrucciones en español)

## 1. Verifica el repositorio remoto
Asegúrate de que tu repositorio existe en:
https://github.com/makinatetanos/checker-crypto

Si no existe, créalo en https://github.com/new con el nombre `checker-crypto`.

---

## 2. Configura el remoto en tu proyecto local
```bash
git remote set-url origin https://github.com/makinatetanos/checker-crypto.git
```

---

## 3. Haz push de tu código y estructura
```bash
git push -u origin main
```
Esto dejará tu rama principal (`main`) publicada en GitHub.

---

## 4. Verifica en GitHub
- Ingresa a https://github.com/makinatetanos/checker-crypto
- Deberías ver todo tu código, carpetas, archivos de configuración, workflows y documentación.

---

## 5. Automatización y plantillas
Ya tienes:
- **Workflow de linting**: revisa automáticamente el estilo del código en cada push/PR.
- **Guía de contribución**: archivo `CONTRIBUTING.md` con instrucciones para nuevos colaboradores.
- **Plantilla de issue de onboarding**: para que nuevos desarrolladores sigan los pasos iniciales.

---

## 6. ¿Cómo crear un nuevo issue de onboarding?
- Ve a la pestaña "Issues" > "New issue" > Elige "[onboarding] Checklist para nuevos colaboradores".
- Marca los pasos a medida que los completes.

---

## 7. ¿Cómo colaborar o contribuir?
1. Haz un **fork** del repositorio y clónalo localmente.
2. Instala las dependencias:
   ```bash
   pip install -r requirements-dev.txt
   ```
3. Ejecuta los tests:
   ```bash
   python -m pytest
   ```
4. Crea una rama para tu feature o corrección:
   ```bash
   git checkout -b mi-nueva-feature
   ```
5. Realiza tus cambios y añade tests.
6. Haz commit y push de tu rama:
   ```bash
   git add .
   git commit -m "feat: descripción de mi cambio"
   git push origin mi-nueva-feature
   ```
7. Abre un **Pull Request** desde GitHub.

---

## 8. Buenas prácticas
- No subas archivos de entorno, secretos ni cachés.
- Sigue la guía de estilo y usa type hints.
- Añade o actualiza la documentación si tu cambio lo requiere.
- Usa mensajes de commit descriptivos y en español o inglés claro.

---

## 9. Automatización extra (opcional)
Puedes crear más workflows en `.github/workflows` para ejecutar tests, deploys, etc.

---

## 10. ¿Dudas o problemas?
- Abre un Issue en GitHub describiendo tu problema.
- Consulta el archivo `CONTRIBUTING.md` para más detalles de colaboración.

---

¿Quieres instrucciones para algo más específico (tests, releases, protección de ramas, etc.)? ¿O una guía rápida para nuevos desarrolladores o ejemplos de mensajes de commit? ¡Pídelo en un Issue o en la discusión del repo!
