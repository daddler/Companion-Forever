"""
Referenzdaten: welcher Schaden war vermeidbar.

WarcraftLogs sagt nur, *wer wodurch* Schaden bekam. Ob ein Treffer
vermeidbar war, ist Spielwissen pro Boss - eine Wertung, keine
Messung. Diese Wertung liegt bewusst hier und nicht im Bot:

- Sie muss für WeintTV und die WeintAcademy identisch sein. Eine
  Tabelle im Analyzer ist genau eine Quelle der Wahrheit.
- Sie ist eine Balance-Meinung und ändert sich mit Schwierigkeitsgrad
  und Taktik. Hier ist sie in einem Diff nachvollziehbar und ohne
  Bot-Deploy korrigierbar.
- Sie ist ohne Netzwerkzugriff testbar.

Wichtigste Entscheidung: das Urteil ist **dreiwertig**. Eine
Fähigkeit, die hier nicht steht, ist VERDICT_UNKNOWN und nicht
"unvermeidbar". Würde Unbekanntes als unvermeidbar gelten, bekäme
jeder Boss ohne Referenzdaten automatisch eine tadellose Bewertung -
und die Tabelle deckt anfangs nur eine Handvoll Bosse ab. Umgekehrt
wäre "unbekannt = vermeidbar" eine Unterstellung.

Nachschlagen läuft wie in analyzer.data.encounters über den
kleingeschriebenen Namen, mit einem beim Import gebauten Index.
Unbekannte Eingaben liefern None und werfen nie.

ABDECKUNG IN FOREVER: NOCH KEINE
--------------------------------

`ENCOUNTER_ABILITIES` ist leer. Die Bosse von Barrow Deeps, Hyjal
Summit und Onyxias Hort sind zum Zeitpunkt dieses Eintrags nicht
veröffentlicht, ihre Mechaniken erst recht nicht - und genau dafür
ist die Dreiwertigkeit oben da: solange nichts hinterlegt ist, ist
jeder Treffer VERDICT_UNKNOWN, `MIN_CLASSIFIED_SHARE` verhindert jede
Aussage über "vermeidbar", und die Oberfläche sagt "nicht
eingeordnet".

Das ist die einzige zulässige Antwort. Eine falsch als vermeidbar
eingeordnete Fähigkeit ist schlimmer als eine Lücke: sie erzeugt
einen Vorwurf gegen einen Spieler, der nichts falsch gemacht hat -
und eine aus einer anderen Spielfassung übernommene Tabelle erzeugt
ihn für jeden.

Die kampfunabhängigen Wahrheiten unten bleiben. Sturzschaden ist in
jeder Fassung dieses Spiels vermeidbar.

Erweitern: einen Eintrag in ENCOUNTER_ABILITIES ergänzen. Die
Fähigkeitsnamen sind die *englischen* aus dem Combat-Log bzw. der
WarcraftLogs-Antwort, `label`/`note` sind der deutsche Text für die
Oberfläche. Die Übersetzungstabelle für Bot-Texte entsteht daraus von
selbst - siehe ABILITY_ALIASES weiter unten.
"""

from __future__ import annotations

from dataclasses import dataclass

from analyzer.models import (
    MECHANIC_DEFENSIVE,
    MECHANIC_INTERRUPT,
    MECHANIC_MOVEMENT,
    MECHANIC_OTHER,
    MECHANIC_POSITIONING,
)


#
# --------------------------------------------------
# Urteile
# --------------------------------------------------
#

VERDICT_AVOIDABLE = "avoidable"
VERDICT_UNAVOIDABLE = "unavoidable"
VERDICT_UNKNOWN = "unknown"


#
# Ab welchem Anteil eingeordneten Schadens eine Aussage über
# "vermeidbar" überhaupt zulässig ist. Darunter fehlen zu viele
# Referenzdaten, und die Academy gibt "keine Daten" statt einer
# Bewertung, die nur die Lücken der Tabelle abbildet.
#

MIN_CLASSIFIED_SHARE = 0.25


@dataclass(frozen=True)
class AbilityRule:
    """
    Die Einordnung einer Fähigkeit.

    `category` ist eine der MECHANIC_*-Konstanten und der Grund,
    warum aus einer Schadenszeile überhaupt ein der Academy
    zuordenbarer Fehler werden kann.

    `note` ist der kurze deutsche Hinweis, was man anders machen
    sollte - er landet unverändert in der Oberfläche.

    `tank_exempt` markiert Fähigkeiten, die für Tanks zum Job
    gehören: einen Nahkampfangriff "vermeidbar" zu nennen, wäre für
    den Tank unsinnig, für alle anderen richtig.
    """

    ability: str

    label: str = ""

    verdict: str = VERDICT_AVOIDABLE

    category: str = MECHANIC_MOVEMENT

    severity: str = "warning"

    note: str = ""

    source_name: str = ""

    tank_exempt: bool = False


#
# --------------------------------------------------
# Kampfunabhängige Wahrheiten
# --------------------------------------------------
#
# Diese gelten überall und sind deshalb aus jeder Bosstabelle
# herausgehalten.
#

GLOBAL_ABILITIES: tuple[AbilityRule, ...] = (

    AbilityRule(
        ability="Falling",
        label="Sturzschaden",
        category=MECHANIC_MOVEMENT,
        note="Sturzschaden lässt sich immer vermeiden.",
    ),
    AbilityRule(
        ability="Fatigue",
        label="Erschöpfung",
        category=MECHANIC_POSITIONING,
        note="Kampfgebiet verlassen - zurück in die Arena.",
    ),
    AbilityRule(
        ability="Drowning",
        label="Ertrinken",
        category=MECHANIC_POSITIONING,
        note="Nicht unter Wasser bleiben.",
    ),
    AbilityRule(
        ability="Melee",
        label="Nahkampfangriff",
        verdict=VERDICT_UNAVOIDABLE,
        category=MECHANIC_OTHER,
        tank_exempt=True,
    ),

)


#
# --------------------------------------------------
# Bossspezifische Einordnung
# --------------------------------------------------
#
# Leer - siehe Modulkommentar. Ein Eintrag hier ist eine Behauptung
# über eine Bossmechanik, und keine davon lässt sich derzeit belegen.
#
# ERWEITERN: je Boss ein Eintrag, Schlüssel ist der Bossname aus dem
# Combat-Log. `ability` ist der englische Fähigkeitsname aus dem Log,
# `label`/`note` der deutsche Text für die Oberfläche. Aufgenommen
# wird nur, was eindeutig ist: Bodenflächen, angekündigte Kegel,
# Zauber mit Unterbrechungsfenster, Tankangriffe. Alles Strittige
# bleibt draussen und damit VERDICT_UNKNOWN.
#
# Der Simulations-Anbieter (analyzer/providers/mock.py) bildet einen
# erfundenen Kampf nach und bringt seine Regeln selbst mit; er ist
# ausdrücklich keine Quelle für diese Tabelle.
#

ENCOUNTER_ABILITIES: dict[str, tuple[AbilityRule, ...]] = {}


#
# EXTRA_ALIASES fängt die Fälle ab, in denen der Bot eine andere
# Formulierung benutzt als das Label hier.
#

EXTRA_ALIASES: dict[str, str] = {}


def _build_aliases() -> dict[str, str]:

    table: dict[str, str] = {}

    for rules in list(ENCOUNTER_ABILITIES.values()) + [GLOBAL_ABILITIES]:

        for rule in rules:

            if not rule.label:
                continue

            table.setdefault(rule.label.strip().lower(), rule.ability)

    table.update(EXTRA_ALIASES)

    return table


ABILITY_ALIASES: dict[str, str] = _build_aliases()


#
# --------------------------------------------------
# Index
# --------------------------------------------------
#
# Beim Import gebaut, damit jedes Nachschlagen ein Dict-Zugriff ist -
# dieselbe Bauart wie in analyzer.data.encounters.
#

_BY_ENCOUNTER: dict[str, dict[str, tuple[AbilityRule, ...]]] = {}

_GLOBAL_INDEX: dict[str, tuple[AbilityRule, ...]] = {}


def _index(rules: tuple[AbilityRule, ...]) -> dict[str, tuple[AbilityRule, ...]]:

    table: dict[str, list[AbilityRule]] = {}

    for rule in rules:

        table.setdefault(rule.ability.lower(), []).append(rule)

    return {key: tuple(value) for key, value in table.items()}


_GLOBAL_INDEX = _index(GLOBAL_ABILITIES)

for _encounter_name, _rules in ENCOUNTER_ABILITIES.items():

    _BY_ENCOUNTER[_encounter_name.lower()] = _index(_rules)


#
# --------------------------------------------------
# Öffentliche API
# --------------------------------------------------
#


def classify(
    encounter_name: str,
    ability: str,
    source_name: str = "",
) -> AbilityRule | None:
    """
    Die Regel zu einer Fähigkeit, oder None wenn keine hinterlegt ist.

    Reihenfolge: Bosstabelle vor globaler Tabelle, und innerhalb der
    Bosstabelle eine auf `source_name` eingeschränkte Regel vor der
    allgemeinen - derselbe Fähigkeitsname kann von mehreren Gegnern
    kommen.
    """

    key = (ability or "").strip().lower()

    if not key:
        return None

    for table in (
        _BY_ENCOUNTER.get((encounter_name or "").strip().lower(), {}),
        _GLOBAL_INDEX,
    ):

        candidates = table.get(key)

        if not candidates:
            continue

        if source_name:

            for candidate in candidates:

                if candidate.source_name == source_name:
                    return candidate

        for candidate in candidates:

            if not candidate.source_name:
                return candidate

        return candidates[0]

    return None


def verdict(
    encounter_name: str,
    ability: str,
    source_name: str = "",
    role: str = "",
) -> str:
    """
    Das Urteil zu einer Fähigkeit - VERDICT_UNKNOWN, wenn nichts
    hinterlegt ist.

    `role` erlaubt die Tank-Ausnahme: was für den Tank zum Job
    gehört, ist für ihn nicht vermeidbar.
    """

    rule = classify(encounter_name, ability, source_name)

    if rule is None:
        return VERDICT_UNKNOWN

    if rule.tank_exempt and role == "tank":
        return VERDICT_UNAVOIDABLE

    return rule.verdict


def is_avoidable(
    encounter_name: str,
    ability: str,
    source_name: str = "",
    role: str = "",
) -> bool:

    return verdict(encounter_name, ability, source_name, role) == VERDICT_AVOIDABLE


def mechanic_category(encounter_name: str, ability: str) -> str:
    """
    Der trainierbare Bereich, dem die Fähigkeit zugeordnet ist.
    """

    rule = classify(encounter_name, ability)

    if rule is None:
        return MECHANIC_OTHER

    return rule.category


def rules_for(encounter_name: str) -> tuple[AbilityRule, ...]:

    return ENCOUNTER_ABILITIES.get(
        _canonical_name(encounter_name),
        (),
    )


def known_encounters() -> tuple[str, ...]:
    """
    Kämpfe mit hinterlegten Referenzdaten - die Oberfläche kann damit
    erklären, warum eine Bewertung fehlt.
    """

    return tuple(sorted(ENCOUNTER_ABILITIES))


def alias_ability(text: str) -> str:
    """
    Der englische Fähigkeitsname zu einem deutschen Fehlertext des
    Bots, oder "" wenn keiner bekannt ist.
    """

    return ABILITY_ALIASES.get((text or "").strip().lower(), "")


def _canonical_name(encounter_name: str) -> str:
    """
    Die Original-Schreibweise eines Bossnamens, unabhängig von der
    Groß-/Kleinschreibung der Eingabe.
    """

    lowered = (encounter_name or "").strip().lower()

    for name in ENCOUNTER_ABILITIES:

        if name.lower() == lowered:
            return name

    return encounter_name or ""
