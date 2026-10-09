"""
Der Umstieg von der alten Companion (Mists of Pandaria) auf diese.

Die alte Companion bekommt die Forever-Fassung als gewöhnliches Update
(siehe `docs/systems/update-system.md`, *Der Umstieg von der alten
Companion*). Gleiche Windows-AppId, gleicher Programmordner, gleiche
Konfigurationsdatei - der Nutzer drückt "Aktualisieren", und beim
nächsten Start läuft diese App mit seinen Einstellungen.

Mit einer Ausnahme: den WoW-Ordner übernimmt sie absichtlich **nicht**
(`Config._migrate_wow_paths()`), und die Suche danach ist für Forever
eine Vermutung (`core/wow_clients.py`). Wer umsteigt, muss also einmal
nachsehen, ob der gefundene Beta-Ordner stimmt, bevor er Codex
installiert. Diese Datei entscheidet nur, *wer* den Hinweis bekommt -
rein rechnend, ohne Qt, damit es sich ohne Fenster prüfen lässt.

WORAN MAN EINEN UMSTEIGER ERKENNT
---------------------------------

An `classic_path`. Jede Konfiguration, die eine Companion bis 4.x je
geschrieben hat, trägt diesen Schlüssel - auch leer, weil er dort zu
den Voreinstellungen gehörte. Diese App legt ihn nie an und löscht ihn
nie. Ein Schlüssel, den nur die alte App schreibt, ist ein besseres
Kennzeichen als `wow_client == "mop_classic"`: den gibt es erst seit
4.1, und wer von 4.0 kommt, hat ihn nicht.
"""

from __future__ import annotations


SEEN_KEY = "forever_switch_notice_seen"


def came_from_old_companion(data: dict) -> bool:

    if "classic_path" in data:
        return True

    paths = data.get("wow_paths")

    return isinstance(paths, dict) and "mop_classic" in paths


def needs_notice(data: dict) -> bool:

    if data.get(SEEN_KEY):
        return False

    return came_from_old_companion(data)
