"""
Der sprachunabhängige Abgleich von Fähigkeitsnamen.

Der Katalog nennt Fähigkeiten englisch, WarcraftLogs liefert sie in
der Sprache des Clients, der den Bericht hochgeladen hat. Genau daran
sind auf der Bot-Seite schon einmal sämtliche Cooldown-Listen
gescheitert (siehe docs/warcraftlogs-bridge.md); hier geht es um
dieselbe Falle in den Prüfkriterien der Academy - mit demselben
Symptom: dauerhaft "keine Daten", ohne dass etwas fehlschlägt.
"""

from analyzer.academy.lessons import all_lessons
from analyzer.data import player_abilities as abilities


UPTIME_METRICS = (
    "dot_uptime",
    "hot_uptime",
    "buff_uptime",
    "cooldown_usage",
    "cooldown_alignment",
    "cooldown_wasted",
)


def test_a_translation_makes_two_names_the_same_ability(monkeypatch):
    """
    Der Zweck der Tabelle, an einem Eintrag vorgeführt.

    Der Eintrag wird hier gesetzt und nicht dem Bestand entnommen: der
    ist leer (Forever ist nicht erschienen), und ein Test, der den
    Bestand vorführt, prüft den Bestand und nicht den Mechanismus. So
    herum bleibt er gültig, egal was später drinsteht.
    """

    monkeypatch.setattr(
        abilities,
        "ABILITY_NAMES",
        {"Shield Block": ("Schildblock", "Schild-Block")},
    )

    monkeypatch.setattr(abilities, "_GROUPS", abilities._build_groups())

    monkeypatch.setattr(abilities, "_CANONICAL", abilities._build_canonical())

    assert abilities.matches("Shield Block", "Schildblock")

    assert abilities.matches("Schildblock", "Shield Block")

    assert abilities.matches("Schildblock", "Schild-Block")

    assert abilities.canonical("Schildblock") == "Shield Block"

    assert abilities.matches("Shield Block", "Schildwall") is False


def test_punctuation_and_case_do_not_matter():
    """
    Doppelpunkte, Apostrophe und Bindestriche schreibt nicht jede
    Quelle gleich - das gilt auch ohne jeden Tabelleneintrag.
    """

    assert abilities.matches("Power Word: Shield", "power word shield")

    assert abilities.matches("Tiger's Fury", "Tigers Fury")

    assert abilities.matches("Anti-Magic Zone", "Anti Magic Zone")

    assert abilities.matches("ANTI-MAGIC ZONE", "anti magic zone")


def test_different_abilities_do_not_match():

    assert abilities.matches("Rip", "Rake") is False

    assert abilities.matches("Shield Block", "Schildwall") is False


def test_an_empty_subject_matches_everything():
    """
    Ein Kriterium ohne Fähigkeitsangabe meint ausdrücklich "alle
    eigenen" - siehe `_uptime` in analyzer/academy/checks.py.
    """

    assert abilities.matches("", "Irgendwas")


def test_unknown_abilities_still_match_themselves():
    """
    Eine Fähigkeit ohne Eintrag ist kein Sonderfall - sie hat nur
    keine Übersetzung.
    """

    assert abilities.matches("Chaos Nova", "chaos nova")

    assert abilities.canonical("Chaos Nova") == "Chaos Nova"

    assert abilities.aliases_of("Chaos Nova") == ("Chaos Nova",)


def test_every_german_name_belongs_to_exactly_one_ability():
    """
    Stünde derselbe deutsche Name bei zwei Fähigkeiten, würde ein
    Kriterium die Wirkungsdauer einer fremden Fähigkeit messen - ein
    falscher Wert ist schlimmer als gar keiner.
    """

    seen: dict[str, str] = {}

    for english, german in abilities.ABILITY_NAMES.items():

        for name in german:

            assert name not in seen, (name, english, seen.get(name))

            seen[name] = english


def test_every_ability_named_in_the_catalogue_is_translated():
    """
    Der eigentliche Wächter: nennt eine Lektion eine Fähigkeit, die
    hier fehlt, ist ihr Kriterium in einem deutschen Bericht
    dauerhaft "keine Daten" - und das sieht in der Oberfläche genauso
    aus wie eine Datenquelle, die den Block gar nicht liefert.
    """

    missing = sorted(
        check.subject
        for lesson in all_lessons()
        for check in lesson.checks
        if check.metric in UPTIME_METRICS
        and check.subject
        and abilities.canonical(check.subject) not in abilities.ABILITY_NAMES
    )

    assert missing == []


def test_the_catalogue_uses_the_english_spelling():
    """
    Englisch ist der Schlüssel: so bleibt eine Lektion lesbar, auch
    wenn sich eine Übersetzung ändert.
    """

    for lesson in all_lessons():

        for check in lesson.checks:

            if check.metric not in UPTIME_METRICS or not check.subject:
                continue

            assert abilities.canonical(check.subject) == check.subject, (
                lesson.lesson_id,
                check.subject,
            )
