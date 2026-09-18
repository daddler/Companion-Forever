"""
Die Spec-Referenztabelle ist eine Datentabelle, und Datentabellen
altern still: eine Spezialisierung, die nie nachgetragen wurde, sieht
in der Oberfläche exakt so aus wie eine, über die die Datenquelle
nichts liefert. Genau diese Verwechslung war der Anlass für die
Tabelle - sie darf hier nicht wieder entstehen.

SEIT 5.0 IST DIE TABELLE LEER
-----------------------------

Und deshalb prüft diese Datei zwei verschiedene Dinge nebeneinander:

1. **Dass die Leere gewollt ist.** Forever überarbeitet jede Klasse;
   die Tabelle aus Mists of Pandaria stehen zu lassen hätte bedeutet,
   Spielern Fähigkeiten vorzuhalten, die es nicht mehr gibt. Der Test
   unten hält diesen Zustand ausdrücklich fest, damit er eine
   Entscheidung bleibt und nicht zu einer vergessenen Lücke wird.

2. **Die Böden, unter die keine Spezialisierung fallen darf, sobald
   sie eingetragen wird.** Die laufen über den Bestand der Tabelle
   und sind heute leer - sie greifen mit dem ersten Eintrag, und
   genau dann werden sie gebraucht. Sie jetzt zu löschen hiesse, sie
   später neu zu erfinden.

Was hier **nicht** mehr steht: die namentlichen Listen aus MoP (die
achtzehn gemeldeten DoTs, die doppelten Schreibweisen, die drei
Inkarnationen). Jede von ihnen war eine Behauptung über einen
bestimmten Zauber; keine davon lässt sich für Forever belegen.
"""

from analyzer.data import class_abilities, player_abilities, specs
from analyzer.models import (
    CD_PERSONAL,
    ROLE_HEALER,
    ROLE_TANK,
    UPTIME_BUFF,
    UPTIME_DOT,
    UPTIME_HOT,
    Actor,
)


def _entry(spec):

    return class_abilities.for_spec(spec.class_name, spec.name)


#
# --------------------------------------------------
# Der Datenstand, ausdrücklich
# --------------------------------------------------
#


def test_the_table_is_empty_and_that_is_on_purpose():
    """
    Fällt dieser Test um, ist die Tabelle gefüllt worden - dann sind
    die Vollständigkeitsprüfungen unten wieder scharf zu stellen
    (siehe `test_a_filled_table_must_cover_every_spec`).
    """

    assert class_abilities.SPEC_ABILITIES == ()

    assert class_abilities.known_specs() == ()


def test_an_empty_table_answers_with_nothing_and_never_with_a_guess():
    """
    Der eigentliche Gegenstand: die Oberfläche muss "keine Angaben"
    zeigen und darf keinen Befund erfinden.
    """

    assert class_abilities.for_spec("Warrior", "Schutz") is None

    assert class_abilities.aura_kind("Schildblock") == ""

    assert class_abilities.translations() == {}


def test_an_unknown_ability_keeps_the_spelling_it_arrived_in():
    """
    Eine Fähigkeit, die diese Tabelle nicht kennt, darf nicht
    verschwinden - sie wird durchgereicht, wie sie gemeldet wurde.
    """

    assert class_abilities.display_name("Zauber XY") == "Zauber XY"

    assert class_abilities.display_name(spell_id=999999) == ""


#
# --------------------------------------------------
# Vollständigkeit - greift, sobald eingetragen wird
# --------------------------------------------------
#


def test_a_filled_table_must_cover_every_spec():
    """
    Halb gefüllt ist der gefährlichste Zustand: die nachgetragenen
    Spezialisierungen bekommen Referenzzeilen, die vergessenen sehen
    aus wie "die Quelle liefert nichts".
    """

    if not class_abilities.SPEC_ABILITIES:
        return

    missing = [
        (spec.class_name, spec.name)
        for spec in specs.SPECS
        if _entry(spec) is None
    ]

    assert missing == []

    assert len(class_abilities.SPEC_ABILITIES) == len(specs.SPECS)


def test_every_spec_brings_cooldowns_that_are_not_optional():
    """
    Optional heißt talentabhängig und wird nie ergänzt. Eine Spec, die
    ausschließlich optionale Einträge hätte, bekäme deshalb nie eine
    einzige Referenzzeile - und wäre von "nicht gepflegt" nicht zu
    unterscheiden.
    """

    for spec in specs.SPECS:

        entry = _entry(spec)

        if entry is None:
            continue

        assert entry.cooldowns, spec

        assert any(
            not cooldown.optional
            for cooldown in entry.cooldowns
        ), spec


def test_tanks_carry_their_active_mitigation():
    """
    Die aktive Schadensminderung ist die eigentliche
    Leistungskennzahl eines Tanks (siehe `_uptime_parts` im
    Evaluator). Fehlt sie, wird ein Tank wieder allein an seiner
    Aktivzeit gemessen.
    """

    for spec in specs.specs_for_role(ROLE_TANK):

        entry = _entry(spec)

        if entry is None:
            continue

        buffs = entry.auras_of(UPTIME_BUFF)

        assert any(not aura.optional for aura in buffs), spec


def test_healers_carry_at_least_one_hot():

    for spec in specs.specs_for_role(ROLE_HEALER):

        entry = _entry(spec)

        if entry is None:
            continue

        hots = entry.auras_of(UPTIME_HOT)

        assert any(not aura.optional for aura in hots), spec


def test_damage_specs_have_either_a_dot_or_a_self_buff():
    """
    Nicht jede Schadensspezialisierung hat einen DoT, aber keine hat
    *nichts* - sonst bliebe die Rotationsbewertung bei der Aktivzeit
    allein stehen.
    """

    for spec in specs.SPECS:

        if spec.role in (ROLE_TANK, ROLE_HEALER):
            continue

        entry = _entry(spec)

        if entry is None:
            continue

        rows = (
            entry.auras_of(UPTIME_DOT)
            + entry.auras_of(UPTIME_BUFF)
            + tuple(
                cooldown
                for cooldown in entry.cooldowns
                if cooldown.category == CD_PERSONAL and not cooldown.optional
            )
        )

        assert rows, spec


#
# --------------------------------------------------
# Innere Widerspruchsfreiheit
# --------------------------------------------------
#


def test_every_ability_has_both_names_and_at_least_one_spell_id():

    for entry in class_abilities.SPEC_ABILITIES:

        for ability in (*entry.auras, *entry.cooldowns):

            assert ability.english.strip(), (entry.spec, ability)

            assert ability.german.strip(), (entry.spec, ability)

            assert ability.spell_ids, (entry.spec, ability)

            assert all(
                isinstance(spell_id, int) and spell_id > 0
                for spell_id in ability.spell_ids
            ), (entry.spec, ability)


def test_a_spell_id_never_names_two_abilities_within_one_spec():
    """
    Zwei Einträge mit derselben ID wären beim Nachschlagen ein
    Münzwurf - und der Verlierer wäre dauerhaft unsichtbar.
    """

    for entry in class_abilities.SPEC_ABILITIES:

        seen: dict[int, str] = {}

        for ability in (*entry.auras, *entry.cooldowns):

            for spell_id in ability.spell_ids:

                previous = seen.setdefault(spell_id, ability.english)

                assert previous == ability.english, (entry.spec, spell_id)


def test_no_spell_id_is_shared_by_two_different_abilities():
    """
    Über alle Spezialisierungen hinweg: zwei Fähigkeiten unter einer
    ID sind ein stiller Fehler, denn die zweite bekommt Namen und
    Abklingzeit der ersten.
    """

    owners: dict[int, str] = {}

    for entry in class_abilities.SPEC_ABILITIES:

        for ability in (*entry.auras, *entry.cooldowns):

            for spell_id in ability.spell_ids:

                previous = owners.setdefault(spell_id, ability.english)

                assert previous == ability.english, (spell_id, ability.english)


def test_each_ability_is_found_by_id_and_by_both_names():

    for entry in class_abilities.SPEC_ABILITIES:

        for kind, abilities in (
            (class_abilities.KIND_AURA, entry.auras),
            (class_abilities.KIND_COOLDOWN, entry.cooldowns),
        ):

            for ability in abilities:

                assert class_abilities.match(
                    entry, spell_id=ability.spell_ids[0], prefer=kind,
                ) is ability

                assert class_abilities.match(
                    entry, ability.english, prefer=kind,
                ) is ability

                assert class_abilities.match(
                    entry, ability.german, prefer=kind,
                ) is ability

                #
                # Schreibweise ist egal: Groß-/Kleinschreibung,
                # Doppelpunkte und Leerzeichen schreibt nicht jede
                # Quelle gleich.
                #

                assert class_abilities.match(
                    entry,
                    ability.english.upper().replace(":", ""),
                    prefer=kind,
                ) is ability


def test_expected_uptimes_stay_within_a_hundred_percent():

    for entry in class_abilities.SPEC_ABILITIES:

        for aura in entry.auras:

            assert 0.0 <= aura.expected_percent <= 100.0, (entry.spec, aura)


#
# --------------------------------------------------
# Anschluss an die übrigen Tabellen
# --------------------------------------------------
#


def test_translations_reach_the_lesson_matching():
    """
    Der Lektionskatalog nennt Fähigkeiten englisch, ein deutscher
    Bericht liefert sie deutsch. Ohne diesen Anschluss wäre jedes
    Kriterium, das eine Fähigkeit nennt, in einem deutschen Log
    dauerhaft "keine Daten" - lautlos.
    """

    for english, german in class_abilities.translations().items():

        for name in german:

            assert player_abilities.matches(english, name), (english, name)


def test_the_spec_follows_from_class_and_role_when_it_is_missing():
    """
    Der Live-Endpunkt schickt für Heiler regelmäßig keine
    Spezialisierung. Wo Klasse und Rolle zusammen eindeutig sind, ist
    das kein Grund, den halben Raid ohne Referenz zu lassen - und wo
    sie es nicht sind, wird nicht geraten.

    Der zweite Teil gilt auch bei leerer Tabelle, und nur er wird hier
    geprüft: beim Priester heilen Disziplin und Heilig beide.
    """

    healing_priest = Actor(
        name="Miraia",
        class_name="Priest",
        spec="",
        role=ROLE_HEALER,
    )

    assert class_abilities.for_actor(healing_priest) is None
