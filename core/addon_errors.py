"""
Die Fehler, die WeintCodex im Spiel gefangen hat.

Seit 6.50.0.0 fängt das Addon seine eigenen Lua-Fehler und vom Spiel
blockierte Aufrufe und hebt die letzten zwanzig über das Neuladen
hinweg auf (`WeintCodex_SavedData.errors`, Aufbau:
`../Codex-Forever/ui/errors.lua`). Im Spiel zeigt `/wcui fehler` sie
zum Kopieren. Hier stehen sie auf dem Desktop, wo Kopieren und
Weiterschicken an den Entwickler einfacher ist als aus einem
Spielfenster.

Der Bericht hat dieselbe Form wie `ER.Lines` im Addon, damit ein
Fehler gleich aussieht, egal woher er kopiert wurde. Was nur der
laufende Client weiss (Spielversion, Klasse, Zone), steht nicht im
Spielstand und fehlt deshalb - es wird nicht erfunden.

Reiner Python-Teil, ohne Qt. Stand des letzten Ausloggens.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from core.lua_reader import LuaReadError, read_variable


VARIABLE = "WeintCodex_SavedData"


@dataclass
class AddonError:

    kind: str

    message: str

    stack: str = ""

    count: int = 1

    first: str = ""

    last: str = ""

    version: str = ""

    account: str = ""

    @property
    def kind_label(self) -> str:

        return "Vom Spiel blockiert" if self.kind == "blocked" else "Lua-Fehler"

    @property
    def headline(self) -> str:

        return (self.message.splitlines() or ["?"])[0]


@dataclass
class AddonErrors:

    known: bool = False

    errors: list = field(default_factory=list)

    error: str = ""


def _text(value) -> str:

    return value if isinstance(value, str) else ""


def parse_errors(saved: dict, account: str = "") -> AddonErrors:
    """Aus dem gelesenen `WeintCodex_SavedData`. Rein, ohne Dateizugriff."""

    if not isinstance(saved, dict):
        return AddonErrors()

    raw = saved.get("errors")

    if not isinstance(raw, dict):
        return AddonErrors(known=isinstance(saved, dict) and bool(saved))

    errors = []

    for index in sorted(k for k in raw if isinstance(k, int)):

        entry = raw[index]

        if not isinstance(entry, dict):
            continue

        count = entry.get("count")

        errors.append(AddonError(
            kind=_text(entry.get("kind")) or "lua",
            message=_text(entry.get("msg")) or "?",
            stack=_text(entry.get("stack")),
            count=int(count) if isinstance(count, (int, float)) and count > 0 else 1,
            first=_text(entry.get("first")),
            last=_text(entry.get("last")),
            version=_text(entry.get("version")),
            account=account,
        ))

    return AddonErrors(known=True, errors=errors)


def report(errors) -> str:
    """Wie `ER.Lines` im Addon - zum Kopieren und Weiterschicken."""

    lines = ["WeintCodex-Fehler (aus der WeintCompanion, Stand des letzten Ausloggens)", ""]

    for i, e in enumerate(errors, 1):

        lines.append(
            f"#{i}  {e.kind_label}  ·  {e.count}x  ·  zuerst {e.first or '?'}, "
            f"zuletzt {e.last or '?'}  ·  Fassung {e.version or '?'}"
        )

        lines.append(e.message)

        if e.stack:
            lines.append(e.stack)

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def read_file(path: Path) -> AddonErrors:

    account = Path(path).parent.parent.name

    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")

    except OSError as exc:
        return AddonErrors(error=f"{path}: {exc}")

    try:
        saved = read_variable(text, VARIABLE)

    except (LuaReadError, RecursionError, IndexError) as exc:
        return AddonErrors(error=f"{Path(path).name}: nicht lesbar ({exc})")

    return parse_errors(saved, account)


def load(wow_path, _addon_path=None) -> AddonErrors:
    """Alle Konten. Liest Dateien - aus einem Thread, nie aus `refresh()`."""

    from core.backup import saved_variable_files

    known, errors, problems = False, [], []

    for path in saved_variable_files(wow_path):

        result = read_file(path)

        known = known or result.known

        errors.extend(result.errors)

        if result.error:
            problems.append(result.error)

    return AddonErrors(known=known, errors=errors, error="; ".join(problems))
