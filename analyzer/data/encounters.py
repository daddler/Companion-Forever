"""
Referenzdaten zu den Raid-Encountern von *World of Warcraft: Forever*.

**Die Bosslisten sind leer, und das ist der aktuelle Datenstand.**
Blizzard hat zum Zeitpunkt dieses Eintrags die drei Schlachtzüge
benannt und ihre Gruppengrösse genannt - wer darin steht, nicht. Eine
erfundene Liste wäre hier schlimmer als eine leere: sie ordnete
Pulls einer Instanz zu, die sie nie gesehen haben, und die Academy
knüpfte Lerninhalte an Bosse, die es nicht gibt. Ein unbekannter Boss
ist in dieser Datei seit jeher **kein Fehlerfall** (siehe unten) -
solange die Listen leer sind, ist schlicht jeder Boss unbekannt, und
die Oberfläche zeigt den Namen aus dem Log.

Sobald die Listen veröffentlicht sind, ist das eine Datenänderung in
dieser Datei und sonst nirgends.

Bewusste Design-Entscheidung: nachgeschlagen wird über den
Encounter-NAMEN, nicht über die Encounter-ID.

Grund: der ENCOUNTER_START-Eintrag des Combat-Logs liefert Name,
Schwierigkeit und Gruppengröße bereits mit. Der Name ist damit die
verlässliche Information, die ohnehin vorliegt - eine eigene
ID-Tabelle wäre eine zweite Wahrheit, die bei jedem Patch
auseinanderlaufen kann. Diese Tabelle ergänzt deshalb nur, was das
Log NICHT mitliefert: zu welcher Instanz ein Boss gehört und in
welcher Reihenfolge er dort steht.

Unbekannte Bosse sind kein Fehlerfall: `lookup()` gibt dann einen
EncounterInfo mit leerer Instanz zurück, und die Oberfläche zeigt
schlicht den Namen aus dem Log an.
"""

from __future__ import annotations

from analyzer.models import EncounterInfo


#
# --------------------------------------------------
# Instanzen
# --------------------------------------------------
#
# Die drei Schlachtzüge des Erscheinungsinhalts. Namen und
# Gruppengrösse sind angekündigt, die Bosse nicht - siehe
# Modulkommentar.
#

BARROW_DEEPS = "Barrow Deeps"

HYJAL_SUMMIT = "Hyjal Summit"

ONYXIAS_LAIR = "Onyxias Hort"


#
# Die vorgesehene Gruppengrösse je Instanz. Sie steht hier und nicht
# bei den Bossen, weil sie das einzige ist, was über die Instanz
# bekannt ist - und weil die Grösse in Forever zur Instanz gehört und
# nicht zum Schwierigkeitsgrad.
#

INSTANCE_SIZES: dict[str, int] = {

    BARROW_DEEPS: 10,
    HYJAL_SUMMIT: 20,
    ONYXIAS_LAIR: 40,

}


#
# Reihenfolge der Bosse je Instanz, in Pull-Reihenfolge.
#
# Leer heisst "noch nicht veröffentlicht", nicht "keine Bosse". Der
# Unterschied ist derselbe wie bei `stars == 0` und `at == -1`: aus
# einer Datenlücke wird kein Befund.
#

INSTANCE_ENCOUNTERS: dict[str, tuple[str, ...]] = {

    BARROW_DEEPS: (),

    HYJAL_SUMMIT: (),

    ONYXIAS_LAIR: (),

}


#
# Umgekehrter Index: Bossname (kleingeschrieben) -> (Instanz, Position)
#

_BY_NAME: dict[str, tuple[str, int]] = {}

for _instance, _bosses in INSTANCE_ENCOUNTERS.items():

    for _position, _boss in enumerate(_bosses, start=1):

        _BY_NAME[_boss.lower()] = (_instance, _position)


#
# --------------------------------------------------
# Schwierigkeitsgrade
# --------------------------------------------------
#
# Die difficultyID aus ENCOUNTER_START.
#
# **Leer, so wie die Bosslisten.** Welche Schwierigkeitsgrade Forever
# kennt und welche Nummern sie tragen, ist nicht veröffentlicht, und
# die Nummern aus früheren Spielfassungen zu übernehmen wäre eine
# Behauptung über eine fremde Tabelle: dieselbe 5 hiess in MoP "10
# Heroisch" und wäre in Forever im Zweifel etwas anderes. Bis dahin
# fällt jede Nummer auf den generischen Text zurück - der nennt die
# Zahl und behauptet nichts.
#

DIFFICULTY_NAMES: dict[int, str] = {}


def difficulty_name(difficulty_id: int) -> str:

    return DIFFICULTY_NAMES.get(
        difficulty_id,
        f"Schwierigkeit {difficulty_id}",
    )


#
# --------------------------------------------------
# Nachschlagen
# --------------------------------------------------
#


def instance_for(name: str) -> str:
    """
    Instanzname zu einem Boss, oder "" wenn unbekannt.
    """

    entry = _BY_NAME.get(name.strip().lower())

    if entry is None:
        return ""

    return entry[0]


def position_for(name: str) -> int:
    """
    Position des Bosses innerhalb seiner Instanz (1-basiert),
    oder 0 wenn unbekannt.
    """

    entry = _BY_NAME.get(name.strip().lower())

    if entry is None:
        return 0

    return entry[1]


def lookup(
    encounter_id: int,
    name: str,
    difficulty_id: int = 0,
    raid_size: int = 0,
) -> EncounterInfo:
    """
    Baut aus den Rohangaben eines ENCOUNTER_START-Eintrags einen
    EncounterInfo und ergänzt die Instanz aus der Tabelle oben.
    """

    return EncounterInfo(
        encounter_id=encounter_id,
        name=name,
        instance=instance_for(name),
        difficulty=(
            difficulty_name(difficulty_id)
            if difficulty_id
            else ""
        ),
        raid_size=raid_size,
    )


def instance_size(instance: str) -> int:
    """
    Vorgesehene Gruppengrösse einer Instanz, oder 0 wenn unbekannt.

    0 heisst "nicht hinterlegt" und nie "allein" - der Aufrufer zeigt
    dafür nichts an, statt eine Null zu schreiben.
    """

    return INSTANCE_SIZES.get(instance, 0)


def all_instances() -> tuple[str, ...]:
    """
    Alle Schlachtzüge in Erscheinungsreihenfolge.
    """

    return tuple(INSTANCE_ENCOUNTERS)


def all_encounter_names() -> tuple[str, ...]:
    """
    Alle bekannten Bossnamen in Instanz- und Pull-Reihenfolge.
    Wird von der Academy für Boss-bezogene Lerninhalte genutzt.

    Solange die Bosslisten leer sind, ist auch diese Auskunft leer -
    und die Academy hat für Bosse dann nichts anzubieten. Das ist die
    richtige Antwort und keine Lücke, die ein Platzhalter füllen
    sollte.
    """

    names: list[str] = []

    for bosses in INSTANCE_ENCOUNTERS.values():

        names.extend(bosses)

    return tuple(names)
