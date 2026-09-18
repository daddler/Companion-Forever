"""
Spielerfähigkeiten in beiden Sprachen.

Der Lektionskatalog nennt Fähigkeiten **englisch** ("Avenging Wrath",
"Shield Block") - das ist die Schreibweise, in der sie überall
dokumentiert sind und in der der Bot sie idealerweise liefert.
WarcraftLogs gibt Fähigkeitsnamen aber in der Sprache des Clients
zurück, der den Bericht hochgeladen hat: bei einer deutschen Gilde
steht dort "Zorn des Rächers" und "Schildblock". Genau dieser Fehler
hat schon einmal dafür gesorgt, dass sämtliche Cooldown-Listen leer
ankamen (siehe docs/warcraftlogs-bridge.md, "Warum die v2-Felder leer
ankamen") - dort ist er auf der Bot-Seite behoben worden, hier
passiert dasselbe für die Prüfkriterien der Academy.

Ohne diese Tabelle wäre jedes Kriterium, das eine bestimmte Fähigkeit
nennt, in einem deutschen Log dauerhaft "keine Daten" - ohne Fehler,
ohne Warnung, und in der Oberfläche nicht davon zu unterscheiden, dass
der Bot den Block gar nicht liefert.

Drei Regeln, nach denen diese Tabelle gepflegt wird:

* **Sie ist additiv.** Ein fehlender Eintrag kostet einen Treffer, er
  erfindet keinen. Wer eine Fähigkeit vermisst, trägt sie nach; nichts
  anderes im System hängt davon ab.
* **Englisch ist der Schlüssel.** Der Katalog schreibt englisch, und
  die kanonische Form ist der englische Name - so bleibt eine Lektion
  lesbar, auch wenn eine Übersetzung sich ändert.
* **Sie ist von analyzer.data.avoidable getrennt.** Dort stehen
  **Boss**fähigkeiten mit einer Wertung ("war das vermeidbar"), hier
  **Spieler**fähigkeiten ganz ohne Wertung. Beides in eine Tabelle zu
  legen hieße, zwei Fragen zu vermischen, die sich unterschiedlich oft
  ändern.

DER DATENSTAND FÜR FOREVER: NOCH KEINER
---------------------------------------

`ABILITY_NAMES` ist leer, aus demselben Grund wie
`analyzer/data/class_abilities.SPEC_ABILITIES`: welche Fähigkeiten es
nach der angekündigten Überarbeitung jeder Klasse noch gibt und wie
sie auf Deutsch heissen, ist nicht veröffentlicht.

Hier wiegt die Leere allerdings leicht, und das ist der Grund, warum
die dritte Regel oben "additiv" heisst: ein fehlender Eintrag kostet
einen Treffer beim Übersetzen, er erfindet keinen. Solange nichts
hinterlegt ist, trifft ein deutsches Log nur da, wo der Bot ohnehin
englisch liefert - dieselbe Lage wie vor dieser Tabelle, und kein
falscher Befund.

Sie lässt sich deshalb auch gefahrlos früh füllen: eine Übersetzung
zu hinterlegen behauptet nicht, dass es die Fähigkeit gibt.
"""

from __future__ import annotations

from analyzer.data import class_abilities


#
# --------------------------------------------------
# Übersetzungen
# --------------------------------------------------
#
# Englischer Name -> deutsche Schreibweisen. Mehrere sind erlaubt:
# einzelne Fähigkeiten sind im Lauf der Erweiterungen umbenannt
# worden, und ein zusätzlicher Eintrag schadet nicht (siehe Regel
# "additiv" oben).
#
# Leer - siehe Modulkommentar. Das ist die eine Tabelle in diesem
# Verzeichnis, die sich schon vor dem Erscheinen füllen lässt.
#

ABILITY_NAMES: dict[str, tuple[str, ...]] = {}


#
# --------------------------------------------------
# Index
# --------------------------------------------------
#


def _key(value: str) -> str:
    """
    Vergleichsform eines Namens.

    Alles außer Buchstaben und Ziffern fällt weg, damit
    "Machtwort: Schild", "Machtwort Schild" und "machtwort:schild"
    denselben Schlüssel ergeben - Doppelpunkte, Apostrophe und
    Bindestriche schreibt nicht jede Quelle gleich.
    """

    return "".join(
        char
        for char in (value or "").casefold()
        if char.isalnum()
    )


def _all_names() -> dict[str, tuple[str, ...]]:
    """
    Diese Tabelle **plus** die Übersetzungen aus
    analyzer/data/class_abilities.py.

    Dort steht ohnehin zu jeder Fähigkeit einer Spezialisierung beides
    - englisch und deutsch -, und zwei Listen derselben Übersetzungen
    laufen unweigerlich auseinander. Das Symptom wäre still: eine
    Lektion, deren Kriterium eine Fähigkeit nennt, die hier fehlt,
    sagt für immer "keine Daten", ohne dass irgendwo ein Fehler
    auftaucht. Die Einträge dieser Datei gewinnen, wo sich beide
    überschneiden - sie sind die von Hand gepflegten.
    """

    merged: dict[str, set[str]] = {
        english: set(german)
        for english, german in class_abilities.translations().items()
    }

    for english, german in ABILITY_NAMES.items():
        merged.setdefault(english, set()).update(german)

    return {
        english: tuple(sorted(german))
        for english, german in merged.items()
    }


def _build_groups() -> dict[str, frozenset[str]]:
    """
    Zu jedem Namensschlüssel die Menge aller gleichbedeutenden
    Schlüssel. Ein Vergleich ist damit ein Mengentest und keine
    Schleife über die ganze Tabelle.
    """

    groups: dict[str, frozenset[str]] = {}

    for english, german in _all_names().items():

        keys = frozenset(
            _key(name)
            for name in (english,) + tuple(german)
            if _key(name)
        )

        for key in keys:
            groups[key] = keys

    return groups


def _build_canonical() -> dict[str, str]:

    table: dict[str, str] = {}

    for english, german in _all_names().items():

        for name in (english,) + tuple(german):
            table[_key(name)] = english

    return table


_GROUPS: dict[str, frozenset[str]] = _build_groups()

_CANONICAL: dict[str, str] = _build_canonical()


#
# --------------------------------------------------
# Abgleich
# --------------------------------------------------
#


def aliases_of(name: str) -> tuple[str, ...]:
    """
    Alle bekannten Schreibweisen einer Fähigkeit, englisch zuerst.
    Unbekanntes liefert sich selbst - eine Fähigkeit ohne Eintrag ist
    kein Sonderfall, sie hat nur keine Übersetzung.
    """

    english = _CANONICAL.get(_key(name))

    if english is None:
        return ((name or "").strip(),) if (name or "").strip() else ()

    return (english,) + ABILITY_NAMES[english]


def canonical(name: str) -> str:
    """
    Der englische Name einer Fähigkeit, oder der Eingabewert.
    """

    return _CANONICAL.get(_key(name), (name or "").strip())


def matches(subject: str, ability: str) -> bool:
    """
    Ob `ability` die in `subject` gemeinte Fähigkeit ist - unabhängig
    von der Sprache.

    Ohne `subject` gilt alles als Treffer: ein Kriterium ohne
    Fähigkeitsangabe meint ausdrücklich "alle eigenen" (siehe
    `_uptime` in analyzer/academy/checks.py).
    """

    wanted = _key(subject)

    if not wanted:
        return True

    found = _key(ability)

    if not found:
        return False

    if wanted == found:
        return True

    return found in _GROUPS.get(wanted, frozenset())


def known_abilities() -> tuple[str, ...]:
    """
    Alle englischen Namen der Tabelle - der Katalogtest hängt daran:
    nennt eine Lektion eine Fähigkeit, die hier fehlt, ist sie in einem
    deutschen Log nicht prüfbar.
    """

    return tuple(sorted(ABILITY_NAMES))
