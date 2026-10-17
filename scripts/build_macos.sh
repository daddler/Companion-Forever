#!/bin/bash
#
# Baut WeintCompanion.app und packt es in dist/WeintCompanion-macOS.dmg.
#
# Läuft auf macOS (lokal oder im CI-Job "macos" in build.yml) und
# braucht neben requirements.txt nur pyinstaller - sips, iconutil und
# hdiutil sind Teil von macOS.
#

set -e

echo ""
echo "========================================"
echo " WeintCompanion macOS Builder"
echo "========================================"
echo ""

rm -rf build dist
mkdir -p build

echo "Erzeuge App-Symbol..."

ICONSET="build/icon.iconset"
mkdir -p "$ICONSET"

for size in 16 32 128 256 512; do
    sips -z $size $size assets/icon.png --out "$ICONSET/icon_${size}x${size}.png" >/dev/null
    double=$((size * 2))
    sips -z $double $double assets/icon.png --out "$ICONSET/icon_${size}x${size}@2x.png" >/dev/null
done

iconutil -c icns "$ICONSET" -o build/icon.icns

echo "Starte PyInstaller..."

pyinstaller --noconfirm WeintCompanion.spec

APP="dist/WeintCompanion.app"

if [ ! -d "$APP" ]; then
    echo "FEHLER: $APP wurde nicht erzeugt."
    exit 1
fi

#
# Ohne Apple-Entwicklerkonto gibt es keine echte Signatur. Eine
# Ad-hoc-Signatur über das ganze Bundle braucht ein Apple-Silicon-Mac
# trotzdem, sonst startet die App dort gar nicht.
#

echo "Signiere ad hoc..."

codesign --force --deep --sign - "$APP"

echo "Erzeuge DMG..."

STAGE="build/dmg"
rm -rf "$STAGE"
mkdir -p "$STAGE"
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"

hdiutil create \
    -volname "WeintCompanion" \
    -srcfolder "$STAGE" \
    -ov \
    -format UDZO \
    dist/WeintCompanion-macOS.dmg

echo ""
echo "Ausgabe: dist/WeintCompanion-macOS.dmg"
