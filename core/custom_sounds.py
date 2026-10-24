"""
Eigene Töne für "Raus da!" im Addon.

Die Companion legt die Dateien des Spielers in ein **eigenes** Addon
`WeintCodex_Sounds` neben WeintCodex - nie in den Ordner `WeintCodex`
selbst: den ersetzt jedes Update vollständig (`core/installer.py`),
und die Töne wären danach weg, ohne dass es jemand bemerkt.

Das Addon liest `WeintCodex_CustomSounds` aus `sounds.lua` erst beim
Gebrauch (`FA.MergeCustom()` in `ui/firealarm.lua`). Vertrag:
`docs/custom-sounds-bridge.md`.

Rein bis auf Dateizugriffe und den einen Aufruf von ffmpeg; keine
Qt-Abhängigkeit, damit es ohne Fenster prüfbar bleibt.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


FOLDER_NAME = "WeintCodex_Sounds"

MANIFEST = "sounds.json"

LUA_FILE = "sounds.lua"

TOC_FILE = f"{FOLDER_NAME}.toc"

#
# Fünf Plätze. Die Schlüssel sind fest (`eigen1` …), weil das Addon
# die Auswahl des Spielers unter diesem Schlüssel speichert: ein
# ersetzter Ton bleibt ausgewählt, ein gelöschter fällt im Addon auf
# den Standard zurück.
#

SLOTS = 5

#
# Ein Alarm ist ein Signal, kein Lied. Länger gekürzt wird nur mit
# ffmpeg; ohne ffmpeg gilt die Größe als Grenze.
#

MAX_SECONDS = 4.0

MAX_BYTES = 2 * 1024 * 1024

#
# WoW spielt Ogg Vorbis zuverlässig; das Addon nimmt nur `.ogg`
# entgegen (Muster in `FA.MergeCustom()`). Alles andere wird mit
# ffmpeg umgewandelt - oder abgelehnt, mit dem Grund.
#

CONVERTIBLE = (".mp3", ".wav", ".flac", ".m4a", ".aac", ".opus", ".wma")

ACCEPTED = (".ogg",) + CONVERTIBLE

#
# Nur Zeichen, die das Spiel und jeder Lua-Stringliteral ohne Escape
# vertragen.
#

_NAME_CLEAN = re.compile(r"[^\w äöüÄÖÜß.,!?()+-]", re.UNICODE)


class SoundError(Exception):
    """Ein Ton liess sich nicht übernehmen - der Text sagt, warum."""


@dataclass(frozen=True)
class CustomSound:

    key: str
    file: str
    name: str
    source: str = ""


def folder(addons_path) -> Path | None:

    if not addons_path:
        return None

    return Path(addons_path) / FOLDER_NAME


def clean_name(text: str, fallback: str) -> str:

    name = _NAME_CLEAN.sub("", str(text or "")).strip()

    return name[:40] or fallback


def ffmpeg_path() -> str | None:

    return shutil.which("ffmpeg")


# --------------------------------------------------
# Lesen
# --------------------------------------------------


def load(addons_path) -> list[CustomSound]:
    """
    Die abgelegten Töne, nach Platz sortiert. Eine fehlende oder
    unlesbare Ablage heißt "keine eigenen Töne", nie ein Fehler.
    Ein Eintrag, dessen Datei fehlt, wird nicht gezeigt.
    """

    base = folder(addons_path)

    if base is None:
        return []

    try:
        raw = json.loads((base / MANIFEST).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []

    out = []

    for entry in raw.get("sounds", []) if isinstance(raw, dict) else []:

        if not isinstance(entry, dict):
            continue

        key = str(entry.get("key") or "")
        file = str(entry.get("file") or "")

        if not re.fullmatch(r"eigen[1-9]", key) or file != f"{key}.ogg":
            continue

        if not (base / file).is_file():
            continue

        out.append(CustomSound(
            key=key,
            file=file,
            name=clean_name(entry.get("name"), key),
            source=str(entry.get("source") or ""),
        ))

    return sorted(out, key=lambda s: s.key)


def free_slot(sounds: list[CustomSound]) -> str | None:

    used = {s.key for s in sounds}

    for i in range(1, SLOTS + 1):

        if f"eigen{i}" not in used:
            return f"eigen{i}"

    return None


# --------------------------------------------------
# Schreiben
# --------------------------------------------------


def _lua_string(text: str) -> str:

    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_lua(sounds: list[CustomSound]) -> str:

    lines = [
        "-- Geschrieben von WeintCompanion. Nicht von Hand ändern -",
        "-- die Companion überschreibt diese Datei.",
        "WeintCodex_CustomSounds = {",
    ]

    for s in sounds:

        lines.append(
            f"    {{ key = {_lua_string(s.key)}, file = {_lua_string(s.file)}, "
            f"text = {_lua_string(s.name)} }},"
        )

    lines.append("}")

    return "\n".join(lines) + "\n"


def interface_line(addons_path) -> str:
    """
    Dieselbe Schnittstellennummer wie das installierte WeintCodex -
    sonst meldet das Spiel den Begleitordner als veraltet. Ohne
    WeintCodex bleibt die Zeile weg (geraten wird sie nicht).
    """

    toc = Path(addons_path) / "WeintCodex" / "WeintCodex.toc"

    try:

        for line in toc.read_text(encoding="utf-8").splitlines():

            if line.startswith("## Interface:"):
                return line.strip()

    except OSError:
        pass

    return ""


def render_toc(addons_path) -> str:

    lines = [interface_line(addons_path)] if interface_line(addons_path) else []

    lines += [
        "## Title: |cff7C6CFFWeintCodex|r Töne",
        "## Notes: Eigene Töne für Raus da!, verwaltet von WeintCompanion",
        "## Author: WeintCompanion",
        LUA_FILE,
    ]

    return "\n".join(lines) + "\n"


def _write(path: Path, text: str) -> None:

    temp = path.with_suffix(path.suffix + ".tmp")

    temp.write_text(text, encoding="utf-8")

    os.replace(temp, path)


def save(addons_path, sounds: list[CustomSound]) -> None:

    base = folder(addons_path)

    if base is None:
        raise SoundError("Kein WoW-Ordner gefunden - erst den Client einrichten.")

    base.mkdir(parents=True, exist_ok=True)

    _write(base / MANIFEST, json.dumps({
        "version": 1,
        "sounds": [
            {"key": s.key, "file": s.file, "name": s.name, "source": s.source}
            for s in sounds
        ],
    }, indent=2, ensure_ascii=False))

    _write(base / LUA_FILE, render_lua(sounds))

    _write(base / TOC_FILE, render_toc(addons_path))


def _is_ogg(path: Path) -> bool:

    try:
        with open(path, "rb") as f:
            return f.read(4) == b"OggS"
    except OSError:
        return False


def convert(source: Path, target: Path, ffmpeg: str) -> None:
    """
    Wandelt in Ogg Vorbis, mono, 44,1 kHz, gekürzt auf MAX_SECONDS,
    mit kurzem Ausblenden am Ende (kein Knacken beim Abschneiden).
    """

    fade_at = max(0.0, MAX_SECONDS - 0.15)

    command = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(source),
        "-t", f"{MAX_SECONDS}",
        "-af", f"afade=t=out:st={fade_at}:d=0.15",
        "-ac", "1", "-ar", "44100",
        "-c:a", "libvorbis", "-q:a", "5",
        str(target),
    ]

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SoundError(f"Die Umwandlung ist gescheitert: {exc}") from exc

    if result.returncode != 0 or not _is_ogg(target):

        detail = (result.stderr or "").strip().splitlines()[-1:] or ["unbekannt"]

        raise SoundError(
            "Die Datei liess sich nicht umwandeln "
            f"({detail[0][:160]})."
        )


def add(addons_path, source, name: str = "", key: str | None = None,
        ffmpeg: str | None = None) -> CustomSound:
    """
    Übernimmt eine Datei in einen Platz (`key`, sonst den ersten
    freien). Ersetzt einen belegten Platz, wenn `key` ihn nennt.
    """

    source = Path(source)

    base = folder(addons_path)

    if base is None:
        raise SoundError("Kein WoW-Ordner gefunden - erst den Client einrichten.")

    if not source.is_file():
        raise SoundError("Die Datei gibt es nicht (mehr).")

    suffix = source.suffix.lower()

    if suffix not in ACCEPTED:
        raise SoundError(
            "Dieses Format kennt die Companion nicht. Möglich sind "
            + ", ".join(s.lstrip(".") for s in ACCEPTED) + "."
        )

    sounds = load(addons_path)

    slot = key or free_slot(sounds)

    if slot is None:
        raise SoundError(
            f"Alle {SLOTS} Plätze sind belegt - erst einen Ton entfernen."
        )

    if not re.fullmatch(r"eigen[1-9]", slot):
        raise SoundError("Unbekannter Platz.")

    base.mkdir(parents=True, exist_ok=True)

    target = base / f"{slot}.ogg"

    temp = base / f"{slot}.neu.ogg"

    if ffmpeg is None:
        ffmpeg = ffmpeg_path()

    try:

        if ffmpeg:

            convert(source, temp, ffmpeg)

        elif suffix == ".ogg" and _is_ogg(source):

            if source.stat().st_size > MAX_BYTES:
                raise SoundError(
                    "Die Datei ist zu groß für einen Warnton (höchstens "
                    "2 MB). Mit ffmpeg kürzt die Companion sie selbst."
                )

            shutil.copyfile(source, temp)

        elif suffix == ".ogg":

            raise SoundError(
                "Die Datei heißt .ogg, ist aber keine Ogg-Datei."
            )

        else:

            raise SoundError(
                f"Für {suffix.lstrip('.')}-Dateien braucht die Companion "
                "ffmpeg (nicht gefunden). Entweder ffmpeg installieren "
                "oder die Datei vorher als .ogg speichern."
            )

        os.replace(temp, target)

    finally:

        if temp.exists():
            try:
                temp.unlink()
            except OSError:
                pass

    sound = CustomSound(
        key=slot,
        file=f"{slot}.ogg",
        name=clean_name(name or source.stem, slot),
        source=source.name,
    )

    save(addons_path, [s for s in sounds if s.key != slot] + [sound])

    return sound


def rename(addons_path, key: str, name: str) -> None:

    sounds = load(addons_path)

    save(addons_path, [
        CustomSound(s.key, s.file, clean_name(name, s.key), s.source)
        if s.key == key else s
        for s in sounds
    ])


def remove(addons_path, key: str) -> None:

    base = folder(addons_path)

    sounds = load(addons_path)

    save(addons_path, [s for s in sounds if s.key != key])

    if base is not None and re.fullmatch(r"eigen[1-9]", key or ""):

        try:
            (base / f"{key}.ogg").unlink()
        except OSError:
            pass
