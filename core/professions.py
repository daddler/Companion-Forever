"""
Berufe aller Charaktere - gelesen aus dem Spielstand des Addons.

Seit WeintCodex 6.14.0.0 merkt sich jeder Charakter, welche Rezepte er
kennt (`WeintCodex_SavedData.professions[Name-Realm].known`, gelesen
aus dem Berufsfenster), seit 1.0.0.0 auch seine Fertigkeit je Beruf
(`skills`, `skillsAt`; Aufbau: `../Codex-Forever/modules/professions.lua`,
`PRO.RememberSkills`). Im Spiel sieht man das nur für den eingeloggten
Charakter - hier stehen alle nebeneinander, für die Frage vor dem
Einloggen: *wer kann das herstellen*, *wo steht mein Schneider*.

Die Namen der Berufe und Rezepte stehen **nicht** im Spielstand,
sondern im Bestand des installierten Addons (`data/professions.lua`,
erzeugt, Herkunft `community`). Diese Datei wird hier nur gelesen, nie
ausgewertet - zwei feste Formen (`P.PROFS`-Zeilen und die Textblöcke in
`P.RAW`), sonst nichts. Fehlt sie, bleiben Rezepte Nummern; geraten
wird kein Name.

`unknown ≠ 0`, wie überall:

* **Fertigkeit unbekannt** (`rank is None`): der Charakter war seit
  1.0.0.0 nicht eingeloggt. Er hat den Beruf trotzdem, wenn er Rezepte
  kennt - angezeigt als "Stufe unbekannt", nie als 0.
* **Rezepte unbekannt** (`scanned is False`): das Berufsfenster war für
  diesen Beruf nie offen. Kein "0 Rezepte".

Reiner Python-Teil, ohne Qt. **Stand, nicht live**: das Spiel schreibt
die Datei beim Ausloggen.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from core.lua_reader import LuaReadError, read_variable


VARIABLE = "WeintCodex_SavedData"


@dataclass
class Recipe:

    spell: int

    name: str

    learn: int | None = None


@dataclass
class ProfessionInfo:

    key: str

    name: str

    category: int = 0

    recipes: dict = field(default_factory=dict)


@dataclass
class CharacterProfession:

    key: str

    name: str

    rank: int | None = None

    max: int | None = None

    scanned: bool = False

    known: list = field(default_factory=list)


@dataclass
class CharacterProfessions:

    label: str

    professions: list = field(default_factory=list)

    skills_at: int = 0


@dataclass
class Professions:

    known: bool = False

    characters: list = field(default_factory=list)

    catalog: dict = field(default_factory=dict)

    error: str = ""

    # --------------------------------------------------

    def recipe_name(self, spell: int) -> str:

        for info in self.catalog.values():

            recipe = info.recipes.get(spell)

            if recipe is not None:
                return recipe.name

        return ""

    def who_can(self, query: str, limit: int = 80) -> list[tuple[str, str, list]]:
        """
        Rezepte, deren Name `query` enthält (oder deren Nummer `query`
        ist): (Rezeptname, Berufsname, [Charaktere]).

        Ohne Bestand des Addons gibt es keine Namen - dann trifft nur
        die Nummer.
        """

        query = (query or "").strip().lower()

        if not query:
            return []

        found: dict[int, list] = {}

        prof_of: dict[int, str] = {}

        for character in self.characters:

            for prof in character.professions:

                for spell in prof.known:

                    name = self.recipe_name(spell)

                    hit = (
                        query == str(spell)
                        if query.isdigit()
                        else query in name.lower()
                    )

                    if hit:
                        found.setdefault(spell, []).append(character.label)
                        prof_of[spell] = prof.name

        rows = [
            (self.recipe_name(spell) or f"Rezept {spell}", prof_of[spell], sorted(chars))
            for spell, chars in found.items()
        ]

        rows.sort(key=lambda r: r[0].lower())

        return rows[:limit]


# --------------------------------------------------
# Bestand des Addons (Namen)
# --------------------------------------------------


_PROF_LINE = re.compile(
    r'\{\s*key\s*=\s*"([^"]+)"[^}]*?cat\s*=\s*(\d+)[^}]*?name\s*=\s*"([^"]+)"\s*\}'
)

_RAW_BLOCK = re.compile(r'\["([^"]+)"\]\s*=\s*\[\[(.*?)\]\]', re.S)


def parse_catalog(text: str) -> dict:
    """
    Aus `data/professions.lua` des Addons. Rein, ohne Dateizugriff.

    Eine Rezeptzeile: `Zauber Gegenstand Lernen ...|Reagenzien|Name`.
    """

    catalog: dict[str, ProfessionInfo] = {}

    for key, cat, name in _PROF_LINE.findall(text or ""):
        catalog[key] = ProfessionInfo(key, name, int(cat))

    for key, body in _RAW_BLOCK.findall(text or ""):

        info = catalog.get(key)

        if info is None:
            continue

        for line in body.splitlines():

            head, _, rest = line.partition("|")

            _reagents, _, name = rest.partition("|")

            parts = head.split()

            if len(parts) < 3 or not parts[0].isdigit() or not name.strip():
                continue

            info.recipes[int(parts[0])] = Recipe(
                int(parts[0]),
                name.strip(),
                int(parts[2]) if parts[2].isdigit() else None,
            )

    return catalog


def load_catalog(addon_path) -> dict:

    if not addon_path:
        return {}

    try:
        text = (Path(addon_path) / "data" / "professions.lua").read_text(
            encoding="utf-8", errors="replace"
        )

    except OSError:
        return {}

    return parse_catalog(text)


# --------------------------------------------------
# Spielstand
# --------------------------------------------------


def _int(value):

    return int(value) if isinstance(value, (int, float)) else None


def parse_professions(saved: dict, catalog: dict | None = None) -> Professions:
    """
    Aus dem gelesenen `WeintCodex_SavedData`. Rein, ohne Dateizugriff.
    """

    catalog = catalog or {}

    if not isinstance(saved, dict) or not isinstance(saved.get("professions"), dict):
        return Professions(catalog=catalog)

    #
    # Rezeptnummer -> Beruf, damit bekannte Rezepte ihrem Beruf
    # zufallen, auch wenn die Fertigkeit unbekannt ist.
    #

    owner = {
        spell: info.key
        for info in catalog.values()
        for spell in info.recipes
    }

    characters = []

    for label, data in saved["professions"].items():

        if not isinstance(label, str) or not isinstance(data, dict):
            continue

        known = data.get("known") if isinstance(data.get("known"), dict) else {}

        scanned = data.get("scanned") if isinstance(data.get("scanned"), dict) else {}

        skills = data.get("skills") if isinstance(data.get("skills"), dict) else {}

        by_key: dict[str, CharacterProfession] = {}

        def entry(key: str) -> CharacterProfession:

            if key not in by_key:

                info = catalog.get(key)

                by_key[key] = CharacterProfession(key, info.name if info else key)

            return by_key[key]

        for key, skill in skills.items():

            if isinstance(key, str) and isinstance(skill, dict):

                prof = entry(key)

                prof.rank = _int(skill.get("rank"))

                prof.max = _int(skill.get("max"))

        for key in scanned:

            if isinstance(key, str):
                entry(key).scanned = True

        for spell, flag in known.items():

            if isinstance(spell, int) and flag is True and spell in owner:
                entry(owner[spell]).known.append(spell)

        if not by_key:
            continue

        def order(prof: CharacterProfession):

            info = catalog.get(prof.key)

            return (info.category if info else 9, prof.name.lower())

        characters.append(CharacterProfessions(
            label=label,
            professions=sorted(by_key.values(), key=order),
            skills_at=_int(data.get("skillsAt")) or 0,
        ))

    characters.sort(key=lambda c: c.label.lower())

    return Professions(known=True, characters=characters, catalog=catalog)


def merge(results) -> Professions:
    """Mehrere Konten: derselbe Charakter zählt einmal, der jüngere gewinnt."""

    known = False

    catalog: dict = {}

    by_label: dict[str, CharacterProfessions] = {}

    errors = []

    for result in results:

        known = known or result.known

        catalog = catalog or result.catalog

        if result.error:
            errors.append(result.error)

        for character in result.characters:

            existing = by_label.get(character.label)

            if existing is None or character.skills_at > existing.skills_at:
                by_label[character.label] = character

    return Professions(
        known=known,
        characters=sorted(by_label.values(), key=lambda c: c.label.lower()),
        catalog=catalog,
        error="; ".join(errors),
    )


def read_file(path: Path, catalog: dict) -> Professions:

    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")

    except OSError as exc:
        return Professions(catalog=catalog, error=f"{path}: {exc}")

    try:
        saved = read_variable(text, VARIABLE)

    except (LuaReadError, RecursionError, IndexError) as exc:
        return Professions(catalog=catalog, error=f"{Path(path).name}: nicht lesbar ({exc})")

    return parse_professions(saved, catalog)


def load(wow_path, addon_path=None) -> Professions:
    """Liest Dateien - aus einem Thread, nie aus `refresh()`."""

    from core.backup import saved_variable_files

    catalog = load_catalog(addon_path)

    return merge(
        [read_file(path, catalog) for path in saved_variable_files(wow_path)]
        or [Professions(catalog=catalog)]
    )
