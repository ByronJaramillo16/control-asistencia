#!/usr/bin/env python3
"""Prepara el proyecto Control de Asistencia.

  python3 scripts/preparar.py web      -> íconos y fuentes en www/ y assets/
  python3 scripts/preparar.py android  -> permisos y firma en el proyecto Android
  python3 scripts/preparar.py ios      -> permisos en el proyecto iOS

Así el repositorio solo guarda texto; las imágenes y los proyectos nativos se generan.
"""
import os, re, shutil, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)
VERDE = (15, 107, 102)


def marca(size, pad, transparente=False):
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0) if transparente else VERDE + (255,))
    d = ImageDraw.Draw(im)
    s = size * (1 - 2 * pad); o = size * pad
    cx, cy = size / 2, o + s * 0.42; r = s * 0.30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255))
    d.polygon([(cx - r * .78, cy + r * .62), (cx + r * .78, cy + r * .62), (cx, cy + r * 1.9)], fill=(255, 255, 255, 255))
    d.line([(cx - r * .45, cy + r * .02), (cx - r * .1, cy + r * .38), (cx + r * .5, cy - r * .35)],
           fill=VERDE + (255,), width=max(2, int(r * .22)), joint="curve")
    return im


def web():
    from PIL import Image
    os.makedirs("assets", exist_ok=True)
    marca(1024, .06).save("assets/icon-only.png")
    marca(1024, .22, True).save("assets/icon-foreground.png")
    Image.new("RGBA", (1024, 1024), VERDE + (255,)).save("assets/icon-background.png")
    sp = Image.new("RGBA", (2732, 2732), VERDE + (255,))
    sp.alpha_composite(marca(700, 0, True), (1016, 980))
    sp.save("assets/splash.png"); sp.save("assets/splash-dark.png")
    marca(192, .06).save("www/icon-192.png")
    marca(512, .06).save("www/icon-512.png")
    marca(180, .06).save("www/apple-touch-icon.png")
    os.makedirs("www/fonts", exist_ok=True)
    for fam, pesos in (("familjen-grotesk", (400, 500, 600, 700)), ("jetbrains-mono", (400, 600))):
        for w in pesos:
            n = f"{fam}-latin-{w}-normal.woff2"
            shutil.copy(f"node_modules/@fontsource/{fam}/files/{n}", f"www/fonts/{n}")
    print("web: íconos y fuentes listos")


def editar(ruta, fn):
    with open(ruta, encoding="utf-8") as f: s = f.read()
    n = fn(s)
    with open(ruta, "w", encoding="utf-8") as f: f.write(n)


def android():
    def manifest(s):
        if "ACCESS_FINE_LOCATION" in s: return s
        extra = ('    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />\n'
                 '    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />\n'
                 '    <uses-permission android:name="android.permission.USE_BIOMETRIC" />\n'
                 '    <uses-feature android:name="android.hardware.location.gps" android:required="false" />\n')
        return s.replace("</manifest>", extra + "</manifest>")
    editar("android/app/src/main/AndroidManifest.xml", manifest)

    def gradle(s):
        if "KEYSTORE_FILE" in s: return s
        s = re.sub(r'versionCode \d+', 'versionCode (System.getenv("VERSION_CODE") ?: "1").toInteger()', s)
        s = re.sub(r'versionName "[^"]*"', 'versionName "1.0." + (System.getenv("VERSION_CODE") ?: "0")', s)
        firma = '''    def ks = System.getenv("KEYSTORE_FILE")
    signingConfigs {
        if (ks) {
            release {
                storeFile file(ks)
                storePassword System.getenv("KEYSTORE_PASSWORD")
                keyAlias System.getenv("KEY_ALIAS")
                keyPassword System.getenv("KEY_PASSWORD")
            }
        }
    }
    buildTypes {
        release {
            if (ks) { signingConfig signingConfigs.release }'''
        return s.replace("    buildTypes {\n        release {", firma, 1)
    editar("android/app/build.gradle", gradle)
    print("android: permisos y firma listos")


def ios():
    def plist(s):
        if "NSLocationWhenInUseUsageDescription" in s: return s
        add = ('\t<key>NSLocationWhenInUseUsageDescription</key>\n'
               '\t<string>Usamos tu ubicación solo al marcar, para verificar que estás en la oficina o en tu lugar de teletrabajo autorizado.</string>\n'
               '\t<key>NSFaceIDUsageDescription</key>\n'
               '\t<string>Usamos Face ID para confirmar que eres tú quien marca la asistencia.</string>\n')
        return s.replace("<dict>\n", "<dict>\n" + add, 1)
    editar("ios/App/App/Info.plist", plist)
    print("ios: permisos listos")


if __name__ == "__main__":
    {"web": web, "android": android, "ios": ios}[sys.argv[1] if len(sys.argv) > 1 else "web"]()
