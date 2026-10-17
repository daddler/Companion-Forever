#!/bin/bash
#
# WeintCompanion macOS-Updater.
#
# Wartet, bis die laufende Companion beendet ist, tauscht das
# .app-Bundle gegen das aus dem heruntergeladenen .dmg und startet
# die neue Fassung. Schlägt der Tausch fehl, kommt die alte Fassung
# zurück an ihren Platz und wird wieder gestartet - eine Companion,
# die nach einem Update gar nicht mehr da ist, wäre der schlechteste
# Ausgang.
#
# Aufruf: updater.sh <aktuelles .app-Bundle> <neues .dmg> <PID>
#

CURRENT="$1"
DMG="$2"
PID="$3"

if [ -z "$CURRENT" ] || [ -z "$DMG" ] || [ -z "$PID" ]; then
    echo "FEHLER: Parameter fehlen! Args: $@"
    exit 1
fi

LOG="$HOME/Library/Logs/WeintCompanion-update.log"
mkdir -p "$(dirname "$LOG")"
exec >>"$LOG" 2>&1

echo "========================================"
echo " WeintCompanion macOS Updater $(date)"
echo "========================================"
echo "Current : $CURRENT"
echo "DMG     : $DMG"
echo "PID     : $PID"

while kill -0 "$PID" 2>/dev/null
do
    sleep 0.2
done

echo "Companion beendet."

MOUNT="$(mktemp -d /tmp/weintcompanion-update.XXXXXX)"

if ! hdiutil attach -nobrowse -readonly -noautoopen -mountpoint "$MOUNT" "$DMG"; then
    echo "FEHLER: DMG konnte nicht eingebunden werden."
    open "$CURRENT"
    exit 1
fi

NEW_APP="$(find "$MOUNT" -maxdepth 1 -name '*.app' -print -quit)"

if [ -z "$NEW_APP" ]; then
    echo "FEHLER: Kein .app-Bundle im DMG."
    hdiutil detach "$MOUNT" -quiet
    open "$CURRENT"
    exit 1
fi

OLD="${CURRENT%.app}.old.app"
rm -rf "$OLD"

if ! mv "$CURRENT" "$OLD"; then
    echo "FEHLER: Alte Fassung lässt sich nicht verschieben (Rechte?)."
    hdiutil detach "$MOUNT" -quiet
    open "$CURRENT"
    exit 1
fi

if ditto "$NEW_APP" "$CURRENT"; then

    echo "Neue Fassung kopiert."
    rm -rf "$OLD"

else

    echo "FEHLER: Kopieren fehlgeschlagen - stelle alte Fassung wieder her."
    rm -rf "$CURRENT"
    mv "$OLD" "$CURRENT"

fi

hdiutil detach "$MOUNT" -quiet
rmdir "$MOUNT" 2>/dev/null

#
# Die Datei kam über die App und nicht über einen Browser - trotzdem
# sicherheitshalber, damit Gatekeeper die neue Fassung nicht erneut
# als "aus dem Internet geladen" zurückhält.
#

xattr -dr com.apple.quarantine "$CURRENT" 2>/dev/null

rm -f "$DMG"

echo "Starte $CURRENT"
open "$CURRENT"
