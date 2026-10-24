# -*- mode: python ; coding: utf-8 -*-

import re
import sys

#
# Die Version aus core/version.py lesen statt sie zu importieren: die
# Spec-Datei läuft nicht zwingend mit dem Projektordner im Suchpfad.
#

VERSION = re.search(
    r'VERSION\s*=\s*"([^"]+)"',
    open("core/version.py", encoding="utf-8").read(),
).group(1)

IS_MACOS = sys.platform == "darwin"

#
# UPX ist überall aus. Auf macOS zerbricht es die Signatur, auf
# Windows hält es die Virenscanner für Packer-Malware: mit UPX
# gepackte PyInstaller-Dateien landen deutlich öfter in Quarantäne.
# Ohne UPX ist der Build etwas größer - mehr kostet es nicht.
#

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[
        # "assets" enthaelt auch assets/fonts - Newsreader, IBM Plex
        # Sans und IBM Plex Mono liegen der App bei und werden beim
        # Start ueber QFontDatabase angemeldet. Ohne sie faellt Qt
        # wortlos auf eine Systemschrift zurueck, und der ganze
        # Entwurf sieht anders aus, ohne dass irgendetwas meldet,
        # dass etwas fehlt (siehe gui/theme/fonts.py).
        ("assets", "assets"),
        ("packaging/linux/updater.sh", "packaging/linux"),
        ("packaging/macos/updater.sh", "packaging/macos"),
        ["resources/icons", "resources/icons"],
        ("CHANGELOG.md", "."),
    ],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        # ffmpeg für die Seite "Töne" (core/custom_sounds.py). Die
        # Programmdatei selbst sammelt der Hook aus
        # pyinstaller-hooks-contrib (hook-imageio_ffmpeg).
        "imageio_ffmpeg",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="WeintCompanion",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # siehe UPX-Kommentar oben
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    #
    # macOS braucht ein .icns; build_macos.sh erzeugt es aus icon.png.
    #
    icon="build/icon.icns" if IS_MACOS else "assets/icon.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,  # siehe UPX-Kommentar oben
    upx_exclude=[],
    name="WeintCompanion",
)
#
# macOS: aus dem Ordner wird ein richtiges WeintCompanion.app-Bundle,
# das build_macos.sh danach in ein .dmg packt.
#

if IS_MACOS:

    app = BUNDLE(
        coll,
        name="WeintCompanion.app",
        icon="build/icon.icns",
        bundle_identifier="de.weint.companion",
        version=VERSION,
        info_plist={
            "CFBundleName": "WeintCompanion",
            "CFBundleDisplayName": "WeintCompanion",
            "CFBundleShortVersionString": VERSION,
            "CFBundleVersion": VERSION,
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "12.0",
        },
    )
