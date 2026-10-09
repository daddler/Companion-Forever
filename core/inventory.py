"""
Der Bestand aller Charaktere - gelesen aus dem Spielstand des Addons.

Seit WeintCodex 6.24.0.0 merkt sich jeder Charakter, was er hat:
Taschen, angelegte Ausrüstung, die Bank (nur solange sie offen war) und
seit 6.26.0.0 sein Gold. Das Addon zeigt es im Tooltip und auf seiner
Seite "Taschen" - aber nur im Spiel, also genau dann nicht, wenn man
den nächsten Abend plant: "wer hat noch Leinenstoff", "wie viel Gold
habe ich insgesamt".

Die Daten stehen in `WeintCodex_SavedData.inventory` in
`WTF/Account/<Konto>/SavedVariables/WeintCodex.lua`
(Aufbau: `../Codex-Forever/ui/inventory.lua`). Diese Datei wird hier
**nur gelesen**, nie geschrieben - geschrieben wird sie vom Spiel beim
Ausloggen, und `upsert_variable()` bleibt die eine Stelle, an der die
App in diese Datei schreibt (für die Zustellung, nicht hierfür).

Drei Unterscheidungen, aus derselben Regel wie im Addon
(`unknown ≠ 0`):

* **Kein Bestand** (`Inventory.known is False`): die Datei fehlt, das
  Addon ist zu alt oder "Bestand merken" ist aus. Das ist kein leerer
  Bestand, und die Seite sagt das.
* **Bank unbekannt** (`bank is None`): die Bank dieses Charakters war
  nie offen. Nicht 0.
* **Gold unbekannt** (`money is None`): dieser Charakter war seit
  6.26.0.0 nicht mehr eingeloggt. Er zählt in keine Summe und wird
  gezählt, nicht verschwiegen.

Reiner Python-Teil, ohne Qt - die Seite liest ihn in `on_enter()`,
nie in `refresh()` (das darf nur zeichnen).

**Stand, nicht live**: was hier steht, ist der Stand des letzten
Ausloggens. Während das Spiel läuft, ändert sich die Datei nicht.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from core.lua_reader import LuaReadError, read_variable


VARIABLE = "WeintCodex_SavedData"


@dataclass
class CharacterStock:

    key: str

    name: str

    realm: str

    class_token: str = ""

    faction: str = ""

    bags: dict = field(default_factory=dict)

    worn: dict = field(default_factory=dict)

    #
    # `None` heisst: nie gesehen. Eine leere Bank ist `{}`.
    #

    bank: dict | None = None

    money: int | None = None

    at: int = 0

    bank_at: int = 0

    money_at: int = 0

    def count(self, item_id: int) -> tuple[int, int, int]:
        """(Taschen, Bank, angelegt) für einen Gegenstand."""

        return (
            self.bags.get(item_id, 0),
            (self.bank or {}).get(item_id, 0),
            self.worn.get(item_id, 0),
        )

    @property
    def label(self) -> str:

        return f"{self.name}-{self.realm}" if self.realm else self.name


@dataclass
class Holder:

    character: CharacterStock

    bags: int

    bank: int

    worn: int

    @property
    def total(self) -> int:

        return self.bags + self.bank + self.worn

    def where(self) -> str:

        parts = []

        if self.bags:
            parts.append(f"Taschen {self.bags}")

        if self.bank:
            parts.append(f"Bank {self.bank}")

        if self.worn:
            parts.append("angelegt")

        return " · ".join(parts)


@dataclass
class ItemStock:

    item_id: int

    name: str

    holders: list

    @property
    def total(self) -> int:

        return sum(holder.total for holder in self.holders)


@dataclass
class Inventory:

    known: bool = False

    characters: list = field(default_factory=list)

    names: dict = field(default_factory=dict)

    #
    # Was beim Lesen schiefging - für das Protokoll und für den
    # Leerzustand der Seite, der sonst "noch nichts gemeldet" sagen
    # würde, wo eine Datei unlesbar war.
    #

    error: str = ""

    # --------------------------------------------------

    def realms(self) -> list[str]:

        return sorted({c.realm for c in self.characters if c.realm})

    def gold(self) -> tuple[int, int]:
        """(Summe in Kupfer, Anzahl Charaktere ohne Goldstand)."""

        total = 0

        unknown = 0

        for character in self.characters:

            if character.money is None:
                unknown += 1

            else:
                total += character.money

        return total, unknown

    def bank_unknown(self) -> int:

        return sum(1 for c in self.characters if c.bank is None)

    def item_ids(self) -> set[int]:

        ids = set()

        for character in self.characters:

            ids.update(character.bags)
            ids.update(character.worn)
            ids.update(character.bank or {})

        return ids

    def item(self, item_id: int) -> ItemStock:

        holders = []

        for character in self.characters:

            bags, bank, worn = character.count(item_id)

            if bags + bank + worn > 0:
                holders.append(Holder(character, bags, bank, worn))

        holders.sort(key=lambda h: (-h.total, h.character.name.lower()))

        return ItemStock(
            item_id,
            self.names.get(item_id, ""),
            holders,
        )

    def search(self, query: str, limit: int = 60) -> list[ItemStock]:
        """
        Gegenstände, deren Name `query` enthält (ohne Gross-/Klein-
        schreibung), oder deren Nummer `query` ist.

        Ein Gegenstand ohne bekannten Namen (das Addon kennt den Namen
        erst, wenn er einmal in einer Tasche lag) ist nur über seine
        Nummer zu finden - geraten wird kein Name.

        Leere Suche: die meistvorhandenen Gegenstände.
        """

        query = (query or "").strip().lower()

        ids = self.item_ids()

        if query.isdigit():

            wanted = int(query)

            matches = [wanted] if wanted in ids else []

        elif query:

            matches = [
                item_id for item_id in ids
                if query in self.names.get(item_id, "").lower()
            ]

        else:

            matches = list(ids)

        items = [self.item(item_id) for item_id in matches]

        if query:
            items.sort(key=lambda i: (i.name.lower() or "~", i.item_id))

        else:
            items.sort(key=lambda i: (-i.total, i.name.lower() or "~"))

        return items[:limit]


# --------------------------------------------------
# Lesen
# --------------------------------------------------


def _counts(raw) -> dict:

    if not isinstance(raw, dict):
        return {}

    out = {}

    for key, value in raw.items():

        if isinstance(key, int) and isinstance(value, (int, float)) and value > 0:
            out[key] = int(value)

    return out


def _int(value, default=0):

    return int(value) if isinstance(value, (int, float)) else default


def parse_inventory(saved: dict) -> Inventory:
    """
    Aus dem gelesenen `WeintCodex_SavedData`. Rein, ohne Dateizugriff.
    """

    if not isinstance(saved, dict):
        return Inventory()

    raw = saved.get("inventory")

    if not isinstance(raw, dict):
        return Inventory()

    names = {}

    for key, value in (raw.get("names") or {}).items():

        if isinstance(key, int) and isinstance(value, str) and value:
            names[key] = value

    characters = []

    for key, data in (raw.get("chars") or {}).items():

        if not isinstance(key, str) or not isinstance(data, dict):
            continue

        realm_part, _, name_part = key.partition("|")

        name = data.get("name") if isinstance(data.get("name"), str) else name_part

        realm = data.get("realm") if isinstance(data.get("realm"), str) else realm_part

        money = data.get("money")

        characters.append(CharacterStock(
            key=key,
            name=name or "?",
            realm=realm or "",
            class_token=data.get("class") if isinstance(data.get("class"), str) else "",
            faction=data.get("faction") if isinstance(data.get("faction"), str) else "",
            bags=_counts(data.get("bags")),
            worn=_counts(data.get("worn")),
            bank=_counts(data.get("bank")) if isinstance(data.get("bank"), dict) else None,
            money=int(money) if isinstance(money, (int, float)) else None,
            at=_int(data.get("at")),
            bank_at=_int(data.get("bankAt")),
            money_at=_int(data.get("moneyAt")),
        ))

    characters.sort(key=lambda c: (c.realm.lower(), c.name.lower()))

    return Inventory(known=True, characters=characters, names=names)


def merge(inventories) -> Inventory:
    """
    Mehrere Konten zu einem Bestand.

    Derselbe Charakter auf zwei Konten (nach einem Kontoumzug) zählt
    einmal: der jüngere Stand gewinnt.
    """

    known = False

    by_key: dict[str, CharacterStock] = {}

    names: dict = {}

    errors = []

    for inventory in inventories:

        known = known or inventory.known

        names.update(inventory.names)

        if inventory.error:
            errors.append(inventory.error)

        for character in inventory.characters:

            existing = by_key.get(character.key)

            if existing is None or character.at > existing.at:
                by_key[character.key] = character

    characters = sorted(
        by_key.values(),
        key=lambda c: (c.realm.lower(), c.name.lower()),
    )

    return Inventory(
        known=known,
        characters=characters,
        names=names,
        error="; ".join(errors),
    )


def read_file(path: Path) -> Inventory:

    try:
        text = Path(path).read_text(encoding="latin-1")

    except OSError as exc:
        return Inventory(error=f"{path}: {exc}")

    try:
        saved = read_variable(text, VARIABLE)

    except (LuaReadError, RecursionError, IndexError) as exc:
        return Inventory(error=f"{Path(path).name}: nicht lesbar ({exc})")

    return parse_inventory(saved)


def load(wow_path) -> Inventory:
    """
    Der Bestand aus allen Konten unter `wow_path`.

    Liest Dateien - deshalb aus `on_enter()` einer Seite, nie aus
    `refresh()`.
    """

    from core.backup import saved_variable_files

    return merge(read_file(path) for path in saved_variable_files(wow_path))


def money_text(copper: int) -> str:
    """Wie `IV.MoneyText` im Addon: "12.345 g 6 s", ohne Bilder."""

    copper = int(copper or 0)

    gold, silver, cop = copper // 10000, (copper % 10000) // 100, copper % 100

    if gold:
        return f"{gold:,}".replace(",", ".") + f" g {silver} s"

    if silver:
        return f"{silver} s {cop} k"

    return f"{cop} k"
