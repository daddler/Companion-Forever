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

#
# 1.4.1: 6 statt 4 s (Wunsch des Besitzers - ein Meme braucht seinen ganzen
# Spruch). Damit ein langer Ton im Spiel nicht jede Sekunde neu startet,
# steht seine Länge als `len` in sounds.lua (Vertrag, FA.Gap im Addon).
#

MAX_SECONDS = 6.0

MAX_BYTES = 2 * 1024 * 1024

#
# Schneiden (5.x/1.4.0): der Spieler wählt Start und Ende im Dialog
# `gui/dialogs/sound_trim.py`. Am Ende blendet der Ton aus, beim Start
# mitten in der Datei kurz ein - sonst knackt es an der Schnittkante.
#

FADE_OUT = 0.15

FADE_IN = 0.02

#
# Die kürzeste sinnvolle Auswahl. Darunter hört man im Spiel nur ein Klicken.
#

MIN_SECONDS = 0.2

_DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")

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
    # Länge in Sekunden, `None` = unbekannt (eine kopierte .ogg ohne ffmpeg).
    length: float | None = None


def folder(addons_path) -> Path | None:

    if not addons_path:
        return None

    return Path(addons_path) / FOLDER_NAME


def clean_name(text: str, fallback: str) -> str:

    name = _NAME_CLEAN.sub("", str(text or "")).strip()

    return name[:40] or fallback


def ffmpeg_path() -> str | None:
    """
    Das mitgelieferte ffmpeg zuerst (seit 5.5.0 über `imageio-ffmpeg`
    in jedem Installer), dann eines im System. Mitgeliefert zuerst,
    weil dessen Fähigkeiten bekannt sind - ein System-ffmpeg kann ohne
    libvorbis gebaut sein.
    """

    try:

        import imageio_ffmpeg

        bundled = imageio_ffmpeg.get_ffmpeg_exe()

        if bundled and Path(bundled).is_file():
            return bundled

    except Exception:
        pass

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
            length=_length(entry.get("length")),
        ))

    return sorted(out, key=lambda s: s.key)


def _length(value) -> float | None:
    """Eine Länge aus der Ablage - nur eine echte Zahl über 0, sonst unbekannt."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None

    return round(float(value), 2) if 0 < value <= 60 else None


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

        length = f", len = {s.length:.2f}" if s.length else ""

        lines.append(
            f"    {{ key = {_lua_string(s.key)}, file = {_lua_string(s.file)}, "
            f"text = {_lua_string(s.name)}{length} }},"
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
            {"key": s.key, "file": s.file, "name": s.name, "source": s.source,
             "length": s.length}
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


def probe_duration(source, ffmpeg: str) -> float | None:
    """
    Länge der Datei in Sekunden - aus der Zeile "Duration:" von ffmpeg
    (ein ffprobe bringt imageio-ffmpeg nicht mit). `None` heißt
    unbekannt, nie 0.
    """

    try:
        result = subprocess.run(
            [ffmpeg, "-hide_banner", "-i", str(source)],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    match = _DURATION_RE.search(result.stderr or "")

    if not match:
        return None

    hours, minutes, seconds = match.groups()

    total = int(hours) * 3600 + int(minutes) * 60 + float(seconds)

    return total if total > 0 else None


def waveform(source, ffmpeg: str, buckets: int = 480, rate: int = 8000,
             limit: float = 600.0) -> list[float]:
    """
    Die Lautstärke über die Zeit, als `buckets` Spitzenwerte 0..1, für
    das Bild im Schneide-Dialog. Dekodiert mono mit `rate` Hz, höchstens
    `limit` Sekunden. Leer, wenn ffmpeg nichts liefert.
    """

    import array
    import sys

    try:
        result = subprocess.run(
            [ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(source),
             "-t", f"{limit}", "-ac", "1", "-ar", str(rate), "-f", "s16le", "-"],
            capture_output=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []

    raw = result.stdout or b""

    raw = raw[: len(raw) - (len(raw) % 2)]

    if not raw:
        return []

    samples = array.array("h")

    samples.frombytes(raw)

    if sys.byteorder == "big":
        samples.byteswap()

    count = len(samples)

    buckets = max(1, min(buckets, count))

    step = count / buckets

    peaks = []

    for i in range(buckets):

        chunk = samples[int(i * step): max(int((i + 1) * step), int(i * step) + 1)]

        peaks.append(max(abs(min(chunk)), abs(max(chunk))) / 32768.0)

    top = max(peaks) or 1.0

    return [p / top for p in peaks]


def clip_window(start: float, end: float | None, duration: float | None = None
                ) -> tuple[float, float]:
    """
    (Start, Länge) aus der Wahl des Spielers: Start nicht negativ und vor
    dem Ende der Datei, Länge zwischen MIN_SECONDS und MAX_SECONDS. Ohne
    Ende gilt Start + MAX_SECONDS.
    """

    start = max(0.0, float(start or 0.0))

    if duration is not None and start >= duration:
        raise SoundError("Der Start liegt hinter dem Ende der Datei.")

    if end is None:
        end = start + MAX_SECONDS

    if duration is not None:
        end = min(float(end), duration)

    length = float(end) - start

    if length < MIN_SECONDS:
        raise SoundError(
            f"Der Ausschnitt ist zu kurz (mindestens {MIN_SECONDS:.1f} s)."
        )

    return start, min(length, MAX_SECONDS)


def convert(source: Path, target: Path, ffmpeg: str, start: float = 0.0,
            length: float = MAX_SECONDS) -> None:
    """
    Wandelt in Ogg Vorbis, mono, 44,1 kHz: der Ausschnitt ab `start`
    über `length` Sekunden (höchstens MAX_SECONDS), mit kurzem Ausblenden
    am Ende und - wenn mitten in der Datei geschnitten wird - kurzem
    Einblenden am Anfang (kein Knacken an der Schnittkante).
    """

    length = min(max(length, MIN_SECONDS), MAX_SECONDS)

    fade = min(FADE_OUT, length / 2)

    filters = [f"afade=t=out:st={max(0.0, length - fade):.3f}:d={fade:.3f}"]

    if start > 0:
        filters.insert(0, f"afade=t=in:st=0:d={FADE_IN}")

    def command(codec: list[str]) -> list[str]:

        return [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-ss", f"{start:.3f}",
            "-i", str(source),
            "-t", f"{length:.3f}",
            # Nur die Tonspur: das Titelbild einer mp3 würde sonst als
            # Theora-Video mit in die .ogg geschrieben - und eine .ogg mit
            # Videospur spielt das Spiel stumm ab (gemessen 1.4.1).
            "-map", "0:a:0", "-vn", "-sn", "-dn", "-map_metadata", "-1",
            "-af", ",".join(filters),
            "-ar", "44100",
            *codec,
            str(target),
        ]

    #
    # libvorbis zuerst. Fehlt er im jeweiligen ffmpeg-Bau, bleibt der
    # eingebaute Vorbis-Kodierer - der kann nur Stereo und gilt als
    # "experimentell", klingt für einen Warnton aber genauso.
    #

    attempts = (
        ["-ac", "1", "-c:a", "libvorbis", "-q:a", "5"],
        ["-ac", "2", "-c:a", "vorbis", "-strict", "experimental"],
    )

    result = None

    for codec in attempts:

        try:
            result = subprocess.run(
                command(codec), capture_output=True, text=True, timeout=60,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise SoundError(f"Die Umwandlung ist gescheitert: {exc}") from exc

        if result.returncode == 0 and _is_ogg(target):
            return

    detail = (result.stderr or "").strip().splitlines()[-1:] or ["unbekannt"]

    raise SoundError(
        "Die Datei liess sich nicht umwandeln "
        f"({detail[0][:160]})."
    )


def add(addons_path, source, name: str = "", key: str | None = None,
        ffmpeg: str | None = None, start: float = 0.0,
        end: float | None = None) -> CustomSound:
    """
    Übernimmt eine Datei in einen Platz (`key`, sonst den ersten
    freien). Ersetzt einen belegten Platz, wenn `key` ihn nennt.
    `start`/`end` (Sekunden): der Ausschnitt aus dem Schneide-Dialog;
    ohne sie die ersten MAX_SECONDS.
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

    length = None

    if ffmpeg is None:
        ffmpeg = ffmpeg_path()

    try:

        if ffmpeg:

            clip_start, clip_length = clip_window(start, end)

            convert(source, temp, ffmpeg, clip_start, clip_length)

            # Die echte Länge: eine kurze Datei endet vor clip_length.
            length = probe_duration(temp, ffmpeg) or clip_length

        elif start or end is not None:

            raise SoundError(
                "Zum Schneiden braucht die Companion ffmpeg (nicht gefunden)."
            )

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
        length=round(length, 2) if length else None,
    )

    save(addons_path, [s for s in sounds if s.key != slot] + [sound])

    return sound


def rename(addons_path, key: str, name: str) -> None:

    sounds = load(addons_path)

    save(addons_path, [
        CustomSound(s.key, s.file, clean_name(name, s.key), s.source, s.length)
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
