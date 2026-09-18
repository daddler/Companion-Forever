"""
Die Spezialisierungen von *World of Warcraft: Forever* - deutsch,
englisch und mit ihrer Rolle.

Forever spielt auf Stufe 60 und mit den drei Talentbäumen je Klasse,
die das Spiel seit seiner ersten Fassung hat. Die Namen unten sind
deshalb **keine Vermutung**: sie stehen seit 2004 fest, und die
Ankündigung nennt ausdrücklich eine Überarbeitung der Bäume, keine
neuen. Was Forever an ihnen ändert - welches Talent wo sitzt, was es
tut -, steht nicht hier, sondern in den Fähigkeitstabellen daneben;
die sind zum Zeitpunkt dieses Eintrags noch nicht belegbar.

Diese Tabelle schließt eine Lücke, die lange still war und deshalb
niemandem auffiel: der Lektionskatalog und die Simulation benutzen die
**deutschen** Bezeichnungen ("Vergeltung", "Gebrechen"),
WarcraftLogs liefert aber die **englischen** ("Retribution",
"Affliction"). Beim Nachschlagen in `SPEC_LESSONS` traf deshalb im
Echtbetrieb kein einziger Schlüssel zu - jeder Spieler bekam
ausschließlich Rollen- und Allgemeinlektionen, und zwar ohne Fehler,
ohne Warnung und ohne dass die Oberfläche etwas anderes gezeigt hätte
als bei einem Spieler, für den tatsächlich nichts hinterlegt ist.

Zweiter Zweck, und der wiegt für die Bewertung noch schwerer: die
**Rolle** lässt sich aus der Spezialisierung ableiten. Fehlt sie in
der Antwort, riet die App bisher aus Schaden und Heilung - und konnte
Tanks grundsätzlich nicht erkennen (siehe `role_name` in
providers/warcraftlogs_payload.py). Ein als Schadensausteiler geführter
Tank wird gegen die Schadensrangliste der Schadensausteiler gemessen
und bekommt dauerhaft einen Stern, obwohl er seine Aufgabe einwandfrei
erfüllt. Mit dieser Tabelle ist "Schutz" oder "Protection" eine
sichere Aussage und kein Ratespiel mehr.

Nachgeschlagen wird über `(Klasse, Spezialisierung)`, denn die
Bezeichnungen allein sind nicht eindeutig: "Heilig" gibt es beim
Paladin und beim Priester, "Schutz" beim Krieger und beim Paladin,
"Wiederherstellung" beim Druiden und beim Schamanen. Ist die Klasse
unbekannt, greift ein zweiter Weg über den Namen allein - aber nur,
wenn alle Kandidaten in der Rolle übereinstimmen. Lieber keine
Aussage als eine falsche.

DER EINE BAUM OHNE ROLLE
------------------------

"Wilder Kampf" des Druiden ist in dieser Fassung des Spiels **beide**
Rollen: dieselben Talente tragen die Katze und den Bären, und welche
davon jemand gerade ist, entscheidet die Gestalt und nicht der Baum.
Er trägt deshalb `ROLE_UNKNOWN` und nicht "Schaden". Das ist keine
Lücke, die noch zu füllen wäre, sondern die richtige Antwort: ein als
Schadensausteiler geführter Bär wird gegen die Schadensrangliste
gemessen und bekommt dauerhaft einen Stern, obwohl er seine Aufgabe
einwandfrei erfüllt - genau der Fehler, gegen den diese Tabelle
angelegt wurde. Die Rolle kommt für ihn aus dem Kampf selbst
(erlittener Schaden, Spott), nicht aus dem Namen.
"""

from __future__ import annotations

from dataclasses import dataclass

from analyzer.models import ROLE_DPS, ROLE_HEALER, ROLE_TANK, ROLE_UNKNOWN


@dataclass(frozen=True)
class Spec:
    """
    Eine Spezialisierung.

    `name` ist die deutsche Schreibweise und zugleich der Schlüssel des
    Lektionskatalogs; `english` die Schreibweise, in der WarcraftLogs
    sie liefert.
    """

    class_name: str

    name: str

    english: str

    role: str

    @property
    def key(self) -> tuple[str, str]:

        return (self.class_name, self.name)


#
# --------------------------------------------------
# Die siebenundzwanzig Spezialisierungen
# --------------------------------------------------
#
# Neun Klassen, je drei Bäume. Vollständig, einschliesslich der reinen
# Schadensbäume - eine Tabelle, die nur Tanks und Heiler kennt, wäre
# genau die Art halber Datenbestand, die später niemand mehr
# nachpflegt.
#

SPECS: tuple[Spec, ...] = (

    Spec("Druid", "Gleichgewicht", "Balance", ROLE_DPS),
    Spec("Druid", "Wilder Kampf", "Feral", ROLE_UNKNOWN),
    Spec("Druid", "Wiederherstellung", "Restoration", ROLE_HEALER),

    Spec("Hunter", "Tierherrschaft", "Beast Mastery", ROLE_DPS),
    Spec("Hunter", "Treffsicherheit", "Marksmanship", ROLE_DPS),
    Spec("Hunter", "Überleben", "Survival", ROLE_DPS),

    Spec("Mage", "Arkan", "Arcane", ROLE_DPS),
    Spec("Mage", "Feuer", "Fire", ROLE_DPS),
    Spec("Mage", "Frost", "Frost", ROLE_DPS),

    Spec("Paladin", "Heilig", "Holy", ROLE_HEALER),
    Spec("Paladin", "Schutz", "Protection", ROLE_TANK),
    Spec("Paladin", "Vergeltung", "Retribution", ROLE_DPS),

    Spec("Priest", "Disziplin", "Discipline", ROLE_HEALER),
    Spec("Priest", "Heilig", "Holy", ROLE_HEALER),
    Spec("Priest", "Schatten", "Shadow", ROLE_DPS),

    Spec("Rogue", "Meucheln", "Assassination", ROLE_DPS),
    Spec("Rogue", "Kampf", "Combat", ROLE_DPS),
    Spec("Rogue", "Täuschung", "Subtlety", ROLE_DPS),

    Spec("Shaman", "Elementar", "Elemental", ROLE_DPS),
    Spec("Shaman", "Verstärkung", "Enhancement", ROLE_DPS),
    Spec("Shaman", "Wiederherstellung", "Restoration", ROLE_HEALER),

    Spec("Warlock", "Gebrechen", "Affliction", ROLE_DPS),
    Spec("Warlock", "Dämonologie", "Demonology", ROLE_DPS),
    Spec("Warlock", "Zerstörung", "Destruction", ROLE_DPS),

    Spec("Warrior", "Waffen", "Arms", ROLE_DPS),
    Spec("Warrior", "Furor", "Fury", ROLE_DPS),
    Spec("Warrior", "Schutz", "Protection", ROLE_TANK),

)


#
# Zusätzliche Schreibweisen, die in Berichten vorkommen. Bewusst
# knapp gehalten: jeder Eintrag hier ist eine Behauptung darüber, wie
# eine Quelle schreibt, und eine falsche Behauptung ordnet einen
# Spieler der falschen Spezialisierung zu.
#

SPEC_ALIASES: dict[str, tuple[str, str]] = {

    #
    # Die zweiteilige Schreibweise desselben Baums, wie sie in älteren
    # Berichten und in WarcraftLogs vorkommt.
    #

    "feralcombat": ("Druid", "Wilder Kampf"),
    "wildheit": ("Druid", "Wilder Kampf"),

    #
    # Berichte, die Gestalt statt Baum melden. Beide zeigen auf
    # denselben Eintrag - und der sagt weiterhin nichts über die
    # Rolle, weil der Baum nichts darüber sagt.
    #

    "feraltank": ("Druid", "Wilder Kampf"),
    "feraldps": ("Druid", "Wilder Kampf"),

    #
    # Umlautfreie Schreibweisen, wie sie aus Exporten und
    # ASCII-Kanälen kommen.
    #

    "ueberleben": ("Hunter", "Überleben"),
    "daemonologie": ("Warlock", "Dämonologie"),
    "verstaerkung": ("Shaman", "Verstärkung"),
    "taeuschung": ("Rogue", "Täuschung"),

    #
    # WarcraftLogs schreibt die zweiteilige Jägerspezialisierung
    # gelegentlich zusammen.
    #

    "beastmaster": ("Hunter", "Tierherrschaft"),

}


#
# --------------------------------------------------
# Index
# --------------------------------------------------
#
# Beim Import gebaut, damit jedes Nachschlagen ein Wörterbuchzugriff
# ist - dieselbe Bauart wie in analyzer.data.encounters und
# analyzer.data.avoidable.
#


def _key(value: str) -> str:
    """
    Vergleichsform eines Namens: kleingeschrieben und ohne alles, was
    nur Schreibweise ist. "Beast Mastery", "beast_mastery" und
    "BeastMastery" werden damit derselbe Schlüssel.
    """

    return "".join(
        char
        for char in (value or "").casefold()
        if char.isalnum()
    )


def _build_index() -> dict[tuple[str, str], Spec]:

    table: dict[tuple[str, str], Spec] = {}

    for spec in SPECS:

        class_key = _key(spec.class_name)

        for name in (spec.name, spec.english):
            table[(class_key, _key(name))] = spec

    for alias, (class_name, name) in SPEC_ALIASES.items():

        for spec in SPECS:

            if spec.class_name == class_name and spec.name == name:
                table[(_key(class_name), _key(alias))] = spec

    return table


def _build_by_name() -> dict[str, tuple[Spec, ...]]:
    """
    Derselbe Bestand ohne Klasse - der Notweg für Antworten, die keine
    Klasse mitschicken.
    """

    table: dict[str, list[Spec]] = {}

    for spec in SPECS:

        for name in (spec.name, spec.english):
            table.setdefault(_key(name), []).append(spec)

    for alias, (class_name, name) in SPEC_ALIASES.items():

        for spec in SPECS:

            if spec.class_name == class_name and spec.name == name:
                table.setdefault(_key(alias), []).append(spec)

    return {key: tuple(value) for key, value in table.items()}


_BY_CLASS: dict[tuple[str, str], Spec] = _build_index()

_BY_NAME: dict[str, tuple[Spec, ...]] = _build_by_name()


#
# --------------------------------------------------
# Nachschlagen
# --------------------------------------------------
#


def find(class_name: str, spec_name: str) -> Spec | None:
    """
    Die Spezialisierung zu Klasse und Bezeichnung, oder None.

    Ohne passende Klasse wird über den Namen allein gesucht - aber nur,
    wenn er eindeutig ist. "Heilig" ohne Klasse bliebe sonst eine
    Münzwurfentscheidung zwischen Paladin und Priester.
    """

    key = _key(spec_name)

    if not key:
        return None

    spec = _BY_CLASS.get((_key(class_name), key))

    if spec is not None:
        return spec

    candidates = _BY_NAME.get(key, ())

    if len(candidates) == 1:
        return candidates[0]

    return None


def normalize_spec(class_name: str, spec_name: str) -> str:
    """
    Die Bezeichnung in der Schreibweise, die der Rest der Anwendung
    benutzt (deutsch).

    Unbekanntes wird **unverändert** durchgereicht statt verworfen: ein
    künftiger Patch soll einen Spieler nicht aus der Auswertung
    entfernen, nur weil die Tabelle ihn noch nicht kennt - dieselbe
    Regel wie bei `class_name()` im Payload-Mapper.
    """

    spec = find(class_name, spec_name)

    if spec is None:
        return (spec_name or "").strip()

    return spec.name


def role_for_spec(class_name: str, spec_name: str) -> str:
    """
    Die Rolle einer Spezialisierung, oder ein leerer String, wenn sie
    sich nicht sicher bestimmen lässt.

    Ist die Klasse unbekannt, zählt der Name allein - aber nur, wenn
    alle Kandidaten dieselbe Rolle haben. "Protection" ist beim Krieger
    wie beim Paladin ein Tank, "Restoration" bei Druide wie Schamane
    Heilung; solche Fälle sind sicher. Eine Bezeichnung, bei der sich
    die Kandidaten unterscheiden, liefert nichts.

    Und "Wilder Kampf" liefert ebenso nichts, obwohl er eindeutig
    gefunden wird: sein Eintrag trägt `ROLE_UNKNOWN`, und der ist hier
    dasselbe wie "keine sichere Aussage" - siehe Modulkommentar.
    """

    spec = find(class_name, spec_name)

    if spec is not None:
        return spec.role if spec.role != ROLE_UNKNOWN else ""

    candidates = _BY_NAME.get(_key(spec_name), ())

    if not candidates:
        return ""

    roles = {entry.role for entry in candidates}

    if len(roles) == 1 and ROLE_UNKNOWN not in roles:
        return candidates[0].role

    return ""


def specs_for_class(class_name: str) -> tuple[Spec, ...]:

    key = _key(class_name)

    return tuple(
        spec
        for spec in SPECS
        if _key(spec.class_name) == key
    )


def specs_for_role(role: str) -> tuple[Spec, ...]:

    return tuple(
        spec
        for spec in SPECS
        if spec.role == role
    )
