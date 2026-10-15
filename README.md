# Control de Asistencia

App de asistencia por geocerca (oficina y teletrabajo) con huella / Face ID.

## Descargar el APK (Android)

Pestaña **Actions** → última ejecución verde de «Compilar app Android» → al final, en **Artifacts**, descarga `Control-Asistencia-vN`. Dentro está el APK para enviar por WhatsApp a los empleados.

Cada cambio que se suba a este repositorio genera un APK nuevo automáticamente. También puedes compilar a mano con **Actions → Compilar app Android → Run workflow**.

## Estructura

- `www/index.html`: la app (ya conectada al servidor de Google Sheets).
- `scripts/preparar.py`: genera íconos, fuentes y permisos nativos.
- `.github/workflows/android.yml`: compila el APK en la nube.

## iPhone (necesita una Mac con Xcode)

```
npm install
pip3 install pillow
python3 scripts/preparar.py web
npm run ios
npx cap open ios
```

## Play Store (opcional)

Agrega los secretos `KEYSTORE_BASE64`, `KEYSTORE_PASSWORD`, `KEY_ALIAS` y `KEY_PASSWORD` en **Settings → Secrets and variables → Actions** y la compilación también generará el `.aab` firmado.
