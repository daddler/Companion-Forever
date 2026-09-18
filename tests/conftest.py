import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from analyzer.data import class_abilities, player_abilities
from analyzer.models import (
    CD_DEFENSIVE,
    CD_PERSONAL,
    CD_RAID,
    UPTIME_BUFF,
    UPTIME_DOT,
    UPTIME_HOT,
)


#
# ==========================================================
# Ein Fähigkeitsbestand zum Vorführen
# ==========================================================
#
# `analyzer/data/class_abilities.py` und
# `analyzer/data/player_abilities.py` sind seit 5.0 leer: Forever
# überarbeitet jede Klasse, und welche Fähigkeiten danach existieren,
# ist nicht veröffentlicht.
#
# Eine Menge Tests prüft aber nicht den *Bestand*, sondern den
# *Mechanismus* - findet ein deutscher Name seine Fähigkeit, bekommt
# ein Cooldown die richtige Schublade, wird eine erwartete, aber nicht
# gemeldete Aura mit Null ergänzt. Ohne Bestand prüfen sie gar nichts
# mehr, und zwar lautlos: sie werden grün, weil nichts passiert.
#
# Dieses Fixture stellt ihnen deshalb einen kleinen, erfundenen
# Bestand hin. Er hat mit Forever nichts zu tun und soll es auch
# nicht - er deckt genau die Formen ab, die der Mechanismus
# unterscheiden muss:
#
#   * ein Tank mit aktiver Schadensminderung (Buff) und zwei
#     Cooldowns in verschiedenen Schubladen,
#   * ein Schadensausteiler mit DoT und persönlichem Cooldown,
#   * ein Heiler mit HoT,
#   * eine talentabhängige (`optional`) Zeile, die nie ergänzt wird,
#   * je englischer und deutscher Name plus eine Spell-ID.
#
# Die Klassen und Spezialisierungen sind echte aus
# `analyzer/data/specs.py` - sonst fände `for_spec()` sie nicht.
#

DEMO_SPECS = (

    class_abilities.SpecAbilities(
        class_name="Warrior",
        spec="Schutz",
        auras=(
            class_abilities.TrackedAura(
                english="Shield Block",
                german="Schildblock",
                spell_ids=(9001,),
                kind=UPTIME_BUFF,
                expected_percent=60.0,
            ),
            class_abilities.TrackedAura(
                english="Shield Barrier",
                german="Schildbarriere",
                spell_ids=(9002,),
                kind=UPTIME_BUFF,
                expected_percent=25.0,
            ),
        ),
        cooldowns=(
            class_abilities.TrackedCooldown(
                english="Shield Wall",
                german="Schildwall",
                spell_ids=(9003,),
                cooldown=300.0,
                category=CD_DEFENSIVE,
            ),
            class_abilities.TrackedCooldown(
                english="Rallying Cry",
                german="Sammelschrei",
                spell_ids=(9004,),
                cooldown=180.0,
                category=CD_RAID,
            ),
        ),
    ),

    class_abilities.SpecAbilities(
        class_name="Warlock",
        spec="Gebrechen",
        auras=(
            class_abilities.TrackedAura(
                english="Corruption",
                german="Verderbnis",
                spell_ids=(9010,),
                kind=UPTIME_DOT,
                expected_percent=95.0,
            ),
            class_abilities.TrackedAura(
                english="Haunt",
                german="Spuk",
                spell_ids=(9011,),
                kind=UPTIME_DOT,
                expected_percent=80.0,
                optional=True,
            ),
        ),
        cooldowns=(
            class_abilities.TrackedCooldown(
                english="Dark Soul",
                german="Dunkle Seele",
                spell_ids=(9012,),
                cooldown=120.0,
                category=CD_PERSONAL,
            ),
        ),
    ),

    class_abilities.SpecAbilities(
        class_name="Druid",
        spec="Wiederherstellung",
        auras=(
            class_abilities.TrackedAura(
                english="Rejuvenation",
                german="Verjüngung",
                spell_ids=(9020,),
                kind=UPTIME_HOT,
                expected_percent=70.0,
            ),
            class_abilities.TrackedAura(
                english="Wild Growth",
                german="Wildwuchs",
                spell_ids=(9022,),
                kind=UPTIME_HOT,
                expected_percent=40.0,
            ),
            class_abilities.TrackedAura(
                english="Lifebloom",
                german="Blühendes Leben",
                spell_ids=(9024,),
                kind=UPTIME_HOT,
                expected_percent=95.0,
            ),
            #
            # Talentabhängig: wird nie ergänzt, auch wenn die Quelle
            # die übrigen HoTs liefert.
            #
            class_abilities.TrackedAura(
                english="Regrowth",
                german="Nachwachsen",
                spell_ids=(9023,),
                kind=UPTIME_HOT,
                expected_percent=20.0,
                optional=True,
            ),
        ),
        cooldowns=(
            class_abilities.TrackedCooldown(
                english="Tranquility",
                german="Seelenruhe",
                spell_ids=(9021,),
                cooldown=180.0,
                category=CD_RAID,
            ),
        ),
    ),

    class_abilities.SpecAbilities(
        class_name="Mage",
        spec="Feuer",
        auras=(
            class_abilities.TrackedAura(
                english="Ignite",
                german="Entzünden",
                spell_ids=(9040,),
                kind=UPTIME_DOT,
                expected_percent=85.0,
            ),
        ),
        cooldowns=(
            class_abilities.TrackedCooldown(
                english="Combustion",
                german="Einäschern",
                spell_ids=(9041,),
                cooldown=45.0,
                category=CD_PERSONAL,
            ),
        ),
    ),

    class_abilities.SpecAbilities(
        class_name="Rogue",
        spec="Meucheln",
        auras=(
            class_abilities.TrackedAura(
                english="Rupture",
                german="Blutung",
                spell_ids=(9030,),
                kind=UPTIME_DOT,
                expected_percent=90.0,
            ),
            class_abilities.TrackedAura(
                english="Deadly Poison",
                german="Tödliches Gift",
                spell_ids=(9031,),
                kind=UPTIME_DOT,
                expected_percent=95.0,
            ),
        ),
        cooldowns=(
            class_abilities.TrackedCooldown(
                english="Vendetta",
                german="Vendetta",
                spell_ids=(9032,),
                cooldown=120.0,
                category=CD_PERSONAL,
            ),
            class_abilities.TrackedCooldown(
                english="Shadow Blades",
                german="Schattenklingen",
                spell_ids=(9033,),
                cooldown=180.0,
                category=CD_PERSONAL,
            ),
            #
            # Situativ: ein ungenutzter Defensivcooldown ist kein
            # verschenkter Einsatz und bekommt deshalb keine
            # Obergrenze.
            #
            class_abilities.TrackedCooldown(
                english="Cloak of Shadows",
                german="Mantel der Schatten",
                spell_ids=(9034,),
                cooldown=90.0,
                category=CD_DEFENSIVE,
            ),
        ),
    ),

)


DEMO_TRANSLATIONS = {
    "Ignite": ("Entzünden",),
    "Combustion": ("Einäschern",),
    "Wild Growth": ("Wildwuchs",),
    "Lifebloom": ("Blühendes Leben",),
    "Regrowth": ("Nachwachsen",),
    "Rupture": ("Blutung",),
    "Deadly Poison": ("Tödliches Gift",),
    "Shadow Blades": ("Schattenklingen",),
    "Cloak of Shadows": ("Mantel der Schatten",),
    "Shield Block": ("Schildblock",),
    "Shield Barrier": ("Schildbarriere",),
    "Shield Wall": ("Schildwall",),
    "Rallying Cry": ("Sammelschrei",),
    "Corruption": ("Verderbnis",),
    "Haunt": ("Spuk",),
    "Dark Soul": ("Dunkle Seele",),
    "Rejuvenation": ("Verjüngung",),
    "Tranquility": ("Seelenruhe",),
}


@pytest.fixture
def demo_abilities(monkeypatch):
    """
    Installiert `DEMO_SPECS` als Fähigkeitsbestand, samt Indizes und
    Übersetzungen, und nimmt ihn danach wieder zurück.
    """

    monkeypatch.setattr(class_abilities, "SPEC_ABILITIES", DEMO_SPECS)

    class_abilities.rebuild_indices()

    monkeypatch.setattr(
        player_abilities, "ABILITY_NAMES", dict(DEMO_TRANSLATIONS)
    )

    monkeypatch.setattr(
        player_abilities, "_GROUPS", player_abilities._build_groups()
    )

    monkeypatch.setattr(
        player_abilities, "_CANONICAL", player_abilities._build_canonical()
    )

    yield DEMO_SPECS

    #
    # monkeypatch setzt `SPEC_ABILITIES` zurück, die Indizes aber
    # nicht - die hängen an einer Funktion und nicht an einem
    # Attribut. Ohne diese Zeile trüge der nächste Test den Bestand
    # von hier weiter.
    #

    monkeypatch.undo()

    class_abilities.rebuild_indices()


#
# ==========================================================
# Ein Lektionskatalog zum Vorführen
# ==========================================================
#
# Derselbe Gedanke wie oben, für `analyzer/academy/lessons/`: die
# Klassen- und Bosslektionen sind leer, weil Forever jede Klasse
# überarbeitet und seine Bosse nicht veröffentlicht sind.
#
# Was dadurch ungeprüft bliebe, ist die **Auswahlreihenfolge** - und
# die ist der Kern des Katalogs: Boss vor Spezialisierung vor Rolle
# vor allgemein. Sie bricht nicht laut, sie liefert einfach die
# falsche Lektion zuerst.
#
# Der Bestand hier ist erfunden. Er hängt an einer echten Klasse und
# einer echten Spezialisierung (sonst fände `lessons_for_actor()` ihn
# nicht) und an dem erfundenen Kampf, den auch die Simulation
# benutzt.
#

from analyzer.academy.lessons import registry as _lesson_registry
from analyzer.academy.lessons import encounters as _encounter_lessons
from analyzer.academy.models import (
    CATEGORY_COOLDOWNS,
    CATEGORY_MECHANICS,
    CATEGORY_ROTATION,
)
from analyzer.academy.models import Lesson as _Lesson


DEMO_SPEC_LESSONS = {

    ("Druid", "Gleichgewicht"): (
        _Lesson(
            lesson_id="druid-balance.rotation.demo",
            title="Beide Dauereffekte halten",
            category=CATEGORY_ROTATION,
            summary="Erfundene Lektion für den Reihenfolgetest.",
            steps=("Nachlegen, bevor sie ablaufen.",),
            class_name="Druid",
            spec="Gleichgewicht",
        ),
    ),

    ("Mage", "Feuer"): (
        _Lesson(
            lesson_id="mage-fire.rotation.demo",
            title="Den Brandeffekt nicht ablaufen lassen",
            category=CATEGORY_ROTATION,
            summary="Erfundene Lektion für den Reihenfolgetest.",
            steps=("Vor Ablauf nachlegen.",),
            class_name="Mage",
            spec="Feuer",
        ),
        #
        # Dieselbe Klasse im Bereich Cooldowns: der Bewerter soll aus
        # einem Defensivbefund die klassenspezifische Lektion wählen
        # und nicht die allgemeine desselben Themas.
        #
        _Lesson(
            lesson_id="mage-fire.cooldowns.demo",
            title="Eisblock einplanen",
            category=CATEGORY_COOLDOWNS,
            summary="Erfundene Lektion für die Auswahlprüfung.",
            steps=("Den Notfallknopf einer Mechanik zuordnen.",),
            class_name="Mage",
            spec="Feuer",
        ),
    ),

    #
    # Der leere Schlüssel gilt für die ganze Klasse.
    #

    ("Druid", ""): (
        _Lesson(
            lesson_id="druid.mechanics.battle_res",
            title="Kampf-Rezz absprechen",
            category=CATEGORY_MECHANICS,
            summary="Erfundene Lektion für den Reihenfolgetest.",
            steps=("Vorher klären, wer sie setzt.",),
            class_name="Druid",
        ),
    ),

}


DEMO_ENCOUNTER_LESSONS = {

    "Übungsziel": (
        _Lesson(
            lesson_id="boss-uebungsziel.mechanics.demo",
            title="Aus dem Inferno gehen",
            category=CATEGORY_MECHANICS,
            summary="Erfundene Lektion für den Reihenfolgetest.",
            steps=("Die Fläche verlassen, bevor sie zündet.",),
            encounter="Übungsziel",
        ),
    ),

}


@pytest.fixture
def demo_lessons(monkeypatch):
    """
    Installiert erfundene Klassen- und Bosslektionen im Katalog.
    """

    monkeypatch.setattr(
        _lesson_registry, "SPEC_LESSONS", dict(DEMO_SPEC_LESSONS)
    )

    monkeypatch.setattr(
        _lesson_registry, "ENCOUNTER_LESSONS", dict(DEMO_ENCOUNTER_LESSONS)
    )

    monkeypatch.setattr(
        _encounter_lessons,
        "ENCOUNTER_LESSONS",
        dict(DEMO_ENCOUNTER_LESSONS),
    )

    return DEMO_SPEC_LESSONS, DEMO_ENCOUNTER_LESSONS


#
# ==========================================================
# Eine Bosswertung zum Vorführen
# ==========================================================
#
# `analyzer/data/avoidable.py` kennt seit 5.0 keinen einzigen Boss:
# die Kämpfe von Forever sind nicht veröffentlicht, und eine aus
# einer anderen Spielfassung übernommene Tabelle würde Spielern
# Vorwürfe für Mechaniken machen, denen sie nie begegnet sind.
#
# Was dadurch ungeprüft bliebe, ist die ganze Kette von "die Quelle
# meldet einen Treffer" bis "die Academy zeigt einen Befund an der
# richtigen Sekunde". Sie hängt an einer Wertung, nicht an einer
# bestimmten.
#
# Der Kampf hier heisst wie der der Simulation und trägt dieselben
# erfundenen Fähigkeiten - so steht im ganzen Projekt genau ein
# erfundener Boss und nicht zwei.
#

from analyzer.data import avoidable as _avoidable
from analyzer.models import (
    MECHANIC_INTERRUPT,
    MECHANIC_MOVEMENT,
    MECHANIC_OTHER,
    MECHANIC_POSITIONING,
)


DEMO_ENCOUNTER = "Übungsziel"


DEMO_RULES = {

    DEMO_ENCOUNTER: (

        _avoidable.AbilityRule(
            ability="Doppelschlag",
            label="Doppelhieb",
            category=MECHANIC_POSITIONING,
            note="Nicht vor dem Boss stehen.",
            tank_exempt=True,
        ),
        _avoidable.AbilityRule(
            ability="Inferno",
            label="Inferno",
            category=MECHANIC_MOVEMENT,
            note="Die brennende Fläche verlassen.",
        ),
        _avoidable.AbilityRule(
            ability="Giftsalve",
            label="Giftsalve",
            category=MECHANIC_INTERRUPT,
            note="Unterbrechen.",
        ),
        _avoidable.AbilityRule(
            ability="Dreifachhieb",
            label="Dreifachhieb",
            verdict=_avoidable.VERDICT_UNAVOIDABLE,
            category=MECHANIC_OTHER,
            tank_exempt=True,
        ),
        _avoidable.AbilityRule(
            ability="Ruf der Nacht",
            label="Ruf der Nacht",
            verdict=_avoidable.VERDICT_UNAVOIDABLE,
            category=MECHANIC_OTHER,
        ),

    ),

}


@pytest.fixture
def demo_rules(monkeypatch):
    """
    Installiert `DEMO_RULES` als Bosswertung, samt Index.
    """

    monkeypatch.setattr(_avoidable, "ENCOUNTER_ABILITIES", dict(DEMO_RULES))

    monkeypatch.setattr(
        _avoidable,
        "_BY_ENCOUNTER",
        {
            name.lower(): _avoidable._index(rules)
            for name, rules in DEMO_RULES.items()
        },
    )

    #
    # Die Aliastabelle entsteht aus den Labels und wird beim Import
    # gebaut - ohne sie erkennt `merge_mechanics()` nicht, dass ein
    # Bot-Befund und ein abgeleiteter denselben Treffer meinen, und
    # zählt ihn doppelt. Genau das prüfen zwei Tests.
    #

    monkeypatch.setattr(
        _avoidable, "ABILITY_ALIASES", _avoidable._build_aliases()
    )

    return DEMO_RULES


#
# ==========================================================
# Ein Schlachtzug zum Vorführen
# ==========================================================
#
# `analyzer/data/encounters.py` kennt die drei Schlachtzüge von
# Forever, aber keinen ihrer Bosse und keinen Schwierigkeitsgrad -
# beides ist nicht veröffentlicht.
#
# Geprüft werden muss trotzdem, dass die Anreicherung greift: dass
# ein Kampfname zu seiner Instanz findet und eine difficultyID zu
# ihrem Namen. Ohne Bestand prüft der Test nur noch, dass nichts
# passiert.
#

from analyzer.data import encounters as _encounters


@pytest.fixture
def demo_encounters(monkeypatch):
    """
    Legt den erfundenen Kampf in Hyjal Summit und benennt eine
    Schwierigkeit.
    """

    table = dict(_encounters.INSTANCE_ENCOUNTERS)

    table[_encounters.HYJAL_SUMMIT] = (DEMO_ENCOUNTER,)

    monkeypatch.setattr(_encounters, "INSTANCE_ENCOUNTERS", table)

    monkeypatch.setattr(
        _encounters,
        "_BY_NAME",
        {DEMO_ENCOUNTER.lower(): (_encounters.HYJAL_SUMMIT, 1)},
    )

    monkeypatch.setattr(
        _encounters, "DIFFICULTY_NAMES", {6: "20 Heroisch"}
    )

    return _encounters.HYJAL_SUMMIT
