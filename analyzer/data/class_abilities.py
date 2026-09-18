"""
Was eine Spezialisierung überhaupt zu zeigen hätte.

Diese Tabelle beantwortet eine Frage, die vorher niemand beantwortet
hat: **welche** DoTs, HoTs, Selbstbuffs und Cooldowns gehören zu einer
Spezialisierung? Ohne sie konnte die Oberfläche nur wiedergeben, was
die Datenquelle geschickt hat - und wenn die nichts geschickt hat,
stand dort "Keine Angaben zu DoT-Uptimes", und zwar wortgleich für

* einen Schurken, der seine Blutung tatsächlich nie aufgelegt hat,
* einen Heiler, dessen HoTs die Quelle nicht mitliefert,
* und einen Kampf, für den es gar keine Tiefenauswertung gibt.

Drei völlig verschiedene Sachverhalte, eine einzige Zeile Text. Genau
deshalb hat diese Tabelle einen eigenen Platz: sie macht aus dem
Schweigen der Quelle eine Aussage, die man lesen kann - "für Meucheln
werden Blutung, Tödliches Gift und Blitzschlag erwartet, gemeldet
wurde davon nichts".

Vier Regeln, nach denen sie gepflegt wird:

* **Drei unabhängige Wege zur Erkennung.** Spell-ID, englischer Name,
  deutscher Name - einer genügt. Denselben Weg geht der Bot seit
  `services/warcraftlogs_spells.py` (siehe docs/warcraftlogs-bridge.md,
  "Warum die v2-Felder leer ankamen"): WarcraftLogs liefert
  Fähigkeitsnamen in der Sprache des Clients, der den Bericht
  hochgeladen hat. Eine falsch erinnerte ID macht einen Eintrag
  deshalb nicht kaputt, solange ein Name passt, und umgekehrt.
* **`optional` heißt: nur zeigen, wenn gemeldet.** Alles, was von
  einem Talent, einer Glyphe oder einem Ausrüstungsteil abhängt, ist
  optional. Eine Zeile "Inkarnation - kein Einsatz" bei einem
  Spieler, der das Talent gar nicht hat, wäre ein Vorwurf für etwas,
  das keiner falsch gemacht hat. Was ohne Talentwahl jeder dieser
  Spezialisierung hat, ist nicht optional - dort ist das Fehlen eine
  echte Aussage.
* **Der Richtwert gehört hierher, nicht in die Oberfläche.** WeintTV
  und die Academy messen denselben Effekt sonst an verschiedenen
  Maßstäben. Neunzig Prozent sind für Blutung mager und für
  Schildblock hervorragend.
* **Sie erfindet keine Zahlen.** Hier steht ausschließlich, was es
  gibt und was gut wäre - nie, was ein Spieler erreicht hat. Das
  bleibt Sache der Datenquelle.

DER DATENSTAND FÜR FOREVER: NOCH KEINER
--------------------------------------

`SPEC_ABILITIES` ist leer. Die Ankündigung zu Forever sagt
ausdrücklich, dass **jede Klasse und jeder Talentbaum überarbeitet**
werden; welche Fähigkeit danach welche Spell-ID trägt, wie lange sie
abklingt und ob es sie überhaupt noch gibt, ist nicht veröffentlicht.

Die Tabelle aus Mists of Pandaria stehen zu lassen wäre der
schlimmste der drei möglichen Zustände. Sie würde nicht schweigen,
sondern etwas Falsches sagen: "für Gleichgewicht werden Eclipse und
Himmlische Ausrichtung erwartet, gemeldet wurde davon nichts" - über
einen Spieler, dessen Klasse diese Fähigkeiten gar nicht mehr hat.
Genau den Satz sollte diese Datei verhindern.

Leer ist dagegen der Zustand, für den sie gebaut ist: `match()` und
`known_specs()` liefern dann nichts, die Oberfläche fällt auf "keine
Angaben" zurück, und niemand bekommt einen Vorwurf.

ERWEITERN: je Spezialisierung ein `SpecAbilities`-Eintrag, in der
Reihenfolge von `analyzer/data/specs.py`. Die Bausteine `_dot`,
`_hot`, `_buff` und `_cd` darunter bleiben unverändert nutzbar - es
ist eine Datenänderung in dieser Datei und sonst nirgends. Wo eine Fähigkeit über mehrere IDs läuft (Talentvarianten,
umbenannte Ränge), stehen sie alle: die Erkennung nimmt die erste, die
passt.
"""

from __future__ import annotations

from dataclasses import dataclass

from analyzer.data import specs as spec_table
from analyzer.models import (
    CD_DEFENSIVE,
    CD_HEAL,
    CD_PERSONAL,
    CD_RAID,
    UPTIME_BUFF,
    UPTIME_DOT,
    UPTIME_HOT,
)


#
# --------------------------------------------------
# Bausteine
# --------------------------------------------------
#


@dataclass(frozen=True)
class TrackedAura:
    """
    Ein Effekt, dessen Wirkungsdauer für diese Spezialisierung zählt.

    `kind` ist einer der UPTIME_*-Werte und entscheidet, in welcher
    der drei Listen des Snapshots der Effekt zu Hause ist - und damit
    auch, für wen die Academy ihn liest (DoTs für Schaden, HoTs für
    Heilung, eigene Buffs für die aktive Schadensminderung der Tanks).
    """

    english: str

    german: str

    spell_ids: tuple[int, ...]

    kind: str = UPTIME_DOT

    expected_percent: float = 0.0

    optional: bool = False

    #
    # Weitere Schreibweisen, unter denen eine Quelle denselben Effekt
    # melden kann. Dieselbe Regel wie in
    # analyzer/data/player_abilities.py: ein zusätzlicher Eintrag
    # schadet nie, ein fehlender kostet einen Treffer.
    #

    aliases: tuple[str, ...] = ()

    @property
    def names(self) -> tuple[str, ...]:

        return (self.english, self.german, *self.aliases)


@dataclass(frozen=True)
class TrackedCooldown:
    """
    Ein Cooldown, dessen Einsätze für diese Spezialisierung zählen.

    `cooldown` ist die Abklingzeit in **Sekunden** - dieselbe Einheit
    wie in `CooldownUsage`, damit aus Kampfdauer und Abklingzeit die
    möglichen Einsätze folgen, ohne dass irgendwo umgerechnet wird.
    """

    english: str

    german: str

    spell_ids: tuple[int, ...]

    cooldown: float = 0.0

    category: str = CD_PERSONAL

    optional: bool = False

    aliases: tuple[str, ...] = ()

    @property
    def names(self) -> tuple[str, ...]:

        return (self.english, self.german, *self.aliases)


@dataclass(frozen=True)
class SpecAbilities:
    """
    Der komplette Referenzbestand einer Spezialisierung.
    """

    class_name: str

    spec: str

    auras: tuple[TrackedAura, ...] = ()

    cooldowns: tuple[TrackedCooldown, ...] = ()

    def auras_of(self, kind: str) -> tuple[TrackedAura, ...]:

        return tuple(
            entry
            for entry in self.auras
            if entry.kind == kind
        )


#
# Kurzformen für die Tabelle unten. Ohne sie wäre jede Zeile dreimal
# so lang und die Tabelle nicht mehr am Stück lesbar - und Lesbarkeit
# ist bei einer Referenztabelle die halbe Pflege.
#


def _dot(
    english, german, ids, expected=95.0, optional=False, aliases=(),
) -> TrackedAura:

    return TrackedAura(
        english=english,
        german=german,
        spell_ids=tuple(ids),
        kind=UPTIME_DOT,
        expected_percent=expected,
        optional=optional,
        aliases=tuple(aliases),
    )


def _hot(
    english, german, ids, expected=85.0, optional=False, aliases=(),
) -> TrackedAura:

    return TrackedAura(
        english=english,
        german=german,
        spell_ids=tuple(ids),
        kind=UPTIME_HOT,
        expected_percent=expected,
        optional=optional,
        aliases=tuple(aliases),
    )


def _buff(
    english, german, ids, expected=0.0, optional=False, aliases=(),
) -> TrackedAura:

    return TrackedAura(
        english=english,
        german=german,
        spell_ids=tuple(ids),
        kind=UPTIME_BUFF,
        expected_percent=expected,
        optional=optional,
        aliases=tuple(aliases),
    )


def _cd(
    english,
    german,
    ids,
    seconds,
    category=CD_PERSONAL,
    optional=False,
    aliases=(),
) -> TrackedCooldown:

    return TrackedCooldown(
        english=english,
        german=german,
        spell_ids=tuple(ids),
        cooldown=float(seconds),
        category=category,
        optional=optional,
        aliases=tuple(aliases),
    )


#
# --------------------------------------------------
# Die Spezialisierungen
# --------------------------------------------------
#
# Leer - siehe Modulkommentar. Reihenfolge beim Füllen wie in
# `analyzer/data/specs.py`, damit sich beide Tabellen nebeneinander
# lesen lassen.
#
# Fähigkeiten, die mehrere Spezialisierungen teilen, gehören
# oberhalb dieser Zeile als eigene `_cd(...)`-Konstante und nicht
# dreimal in die Tabelle: eine Abklingzeit, die an drei Stellen
# steht, steht früher oder später an zwei Stellen falsch.
#

SPEC_ABILITIES: tuple[SpecAbilities, ...] = ()


#
# --------------------------------------------------
# Index
# --------------------------------------------------
#
# Beim Import gebaut - dieselbe Bauart wie in analyzer/data/specs.py
# und analyzer/data/avoidable.py. Jedes Nachschlagen ist danach ein
# Wörterbuchzugriff, was zählt: die Anreicherung läuft bei einer
# Wiedergabe viermal je Sekunde über alle 25 Spieler.
#


def _key(value: str) -> str:
    """
    Vergleichsform eines Namens: kleingeschrieben, ohne Leerzeichen und
    Satzzeichen. "Machtwort: Schild", "machtwort schild" und
    "MACHTWORT:SCHILD" werden damit derselbe Schlüssel.
    """

    return "".join(
        char
        for char in (value or "").casefold()
        if char.isalnum()
    )


def normalize_name(value: str) -> str:
    """
    Die Vergleichsform eines Fähigkeitsnamens - öffentlich, weil die
    Anreicherung (analyzer/analysis/spec_reference.py) dieselbe Form
    braucht, um gemeldete und erwartete Zeilen als dieselbe Fähigkeit
    zu erkennen. Zwei Schreibweisen dieser Normalisierung wären zwei
    Ergebnisse.
    """

    return _key(value)


def _build_index() -> dict[tuple[str, str], SpecAbilities]:

    table: dict[tuple[str, str], SpecAbilities] = {}

    for entry in SPEC_ABILITIES:

        spec = spec_table.find(entry.class_name, entry.spec)

        #
        # Über die Spec-Tabelle indizieren statt über die eigene
        # Schreibweise: dort stehen englische Namen, Umlautvarianten
        # und die Aliase, die WarcraftLogs tatsächlich schickt. Zwei
        # getrennte Namenslisten wären genau die Art Doppelpflege, an
        # der die Spec-Erkennung schon einmal still gescheitert ist.
        #

        names = (
            (spec.name, spec.english)
            if spec is not None
            else (entry.spec,)
        )

        for name in names:
            table[(_key(entry.class_name), _key(name))] = entry

    return table


def _build_aura_index() -> dict[int, TrackedAura]:

    table: dict[int, TrackedAura] = {}

    for entry in SPEC_ABILITIES:

        for aura in entry.auras:

            for spell_id in aura.spell_ids:
                table.setdefault(spell_id, aura)

    return table


def _build_name_index() -> dict[str, TrackedAura]:

    table: dict[str, TrackedAura] = {}

    for entry in SPEC_ABILITIES:

        for aura in entry.auras:

            for name in aura.names:
                table.setdefault(_key(name), aura)

    return table


def _build_ability_index() -> tuple[dict[int, object], dict[str, object]]:
    """
    Auren **und** Cooldowns über alle Specs - der spec-unabhängige
    Weg, den `display_name()` braucht: eine Raid-Cooldown-Liste nennt
    ihren Wirker, aber nicht dessen Spezialisierung.
    """

    by_id: dict[int, object] = {}

    by_name: dict[str, object] = {}

    for entry in SPEC_ABILITIES:

        for ability in (*entry.auras, *entry.cooldowns):

            for spell_id in ability.spell_ids:
                by_id.setdefault(spell_id, ability)

            for name in ability.names:
                by_name.setdefault(_key(name), ability)

    return by_id, by_name


#
# --------------------------------------------------
# Nachschlagen
# --------------------------------------------------
#


def for_spec(class_name: str, spec_name: str) -> SpecAbilities | None:
    """
    Der Referenzbestand einer Spezialisierung, oder None.

    Unbekanntes liefert None statt einer leeren Hülle: "diese Spec
    kenne ich nicht" und "diese Spec hat nichts" sind verschiedene
    Aussagen, und nur die erste darf die Anreicherung stillhalten
    lassen.
    """

    spec = spec_table.find(class_name, spec_name)

    if spec is not None:

        found = _BY_SPEC.get((_key(spec.class_name), _key(spec.name)))

        if found is not None:
            return found

    return _BY_SPEC.get((_key(class_name), _key(spec_name)))


def for_actor(actor) -> SpecAbilities | None:
    """
    Derselbe Zugriff für einen Spieler aus dem Snapshot.

    Fehlt die Spezialisierung, entscheidet **Klasse und Rolle** - aber
    nur, wenn beide zusammen eindeutig sind: ein heilender Druide kann
    nur Wiederherstellung sein, ein Krieger, der tankt, nur Schutz.
    Ein heilender Priester dagegen ist Disziplin *oder* Heilig, und
    dann bleibt es bei "unbekannt". Diese Rückfallebene ist nicht
    kosmetisch: eine Quelle, die `spec` nicht mitschickt (der
    Live-Endpunkt tut das für Heiler regelmäßig), bekäme sonst für
    ihren halben Raid keine einzige Referenzzeile.
    """

    class_name = getattr(actor, "class_name", "")

    found = for_spec(class_name, getattr(actor, "spec", ""))

    if found is not None:
        return found

    role = getattr(actor, "role", "")

    if not role:
        return None

    candidates = [
        spec
        for spec in spec_table.specs_for_class(class_name)
        if spec.role == role
    ]

    if len(candidates) != 1:
        return None

    return for_spec(candidates[0].class_name, candidates[0].name)


#
# Wonach `match()` sucht. Manche Fähigkeiten sind beides: "Schutz"
# des Braumeisters ist ein Cooldown, den man drückt, **und** ein
# Schild mit einer Wirkungsdauer - unter derselben Spell-ID. Ohne
# diese Angabe entschiede die Reihenfolge im Verzeichnis, welcher der
# beiden Einträge zurückkommt, und die gemeldete Cooldown-Zeile bekäme
# die Abklingzeit einer Aura, also keine.
#

KIND_AURA = "aura"

KIND_COOLDOWN = "cooldown"


def _build_spec_lookup() -> dict[tuple[str, str], dict]:
    """
    Je Spezialisierung ein Verzeichnis nach Spell-ID und nach
    Namensschlüssel, getrennt nach Auren und Cooldowns.

    Beim Import gebaut, weil `match()` im heißen Pfad liegt: bei einer
    Wiedergabe läuft die Anreicherung viermal je Sekunde über bis zu
    150 gemeldete Zeilen. Als lineare Suche mit
    Namensnormalisierung je Vergleich war das der teuerste Posten
    eines Bildes.
    """

    table: dict[tuple[str, str], dict] = {}

    for entry in SPEC_ABILITIES:

        index = {
            KIND_AURA: ({}, {}),
            KIND_COOLDOWN: ({}, {}),
        }

        for kind, abilities in (
            (KIND_AURA, entry.auras),
            (KIND_COOLDOWN, entry.cooldowns),
        ):

            by_id, by_name = index[kind]

            for ability in abilities:

                for spell_id in ability.spell_ids:
                    by_id.setdefault(spell_id, ability)

                for name in ability.names:
                    by_name.setdefault(_key(name), ability)

        table[(entry.class_name, entry.spec)] = index

    return table


#
# --------------------------------------------------
# Die Indizes aufbauen
# --------------------------------------------------
#
# In einer Funktion und nicht als fünf Zuweisungen auf Modulebene:
# damit gibt es **eine** Stelle, an der der Bestand in die Indizes
# übergeht, und sie lässt sich ein zweites Mal ausführen.
#
# Das Zweite ist der Grund. Die Tabelle ist derzeit leer (Forever ist
# nicht erschienen), und ein Test, der den Mechanismus vorführen will
# - findet ein deutscher Name seine Fähigkeit, bekommt ein Cooldown
# die richtige Schublade -, muss sich einen Bestand hinstellen können,
# ohne diese Datei zu verändern. Ohne diesen einen Aufruf hinge er an
# fünf privaten Namen und daran, sie in der richtigen Reihenfolge neu
# zu setzen.
#


_BY_SPEC: dict[tuple[str, str], SpecAbilities] = {}

_AURA_BY_ID: dict[int, TrackedAura] = {}

_AURA_BY_NAME: dict[str, TrackedAura] = {}

_BY_ID: dict[int, object] = {}

_BY_NAME_ANY: dict[str, object] = {}

_SPEC_LOOKUP: dict[tuple[str, str], dict] = {}


def rebuild_indices() -> None:
    """
    Die Indizes aus `SPEC_ABILITIES` neu aufbauen.

    Wird beim Import einmal gerufen. Wer `SPEC_ABILITIES` zur Laufzeit
    ersetzt, ruft sie danach erneut - sonst antworten die Indizes
    weiter aus dem alten Bestand.
    """

    global _BY_SPEC, _AURA_BY_ID, _AURA_BY_NAME
    global _BY_ID, _BY_NAME_ANY, _SPEC_LOOKUP

    _BY_SPEC = _build_index()

    _AURA_BY_ID = _build_aura_index()

    _AURA_BY_NAME = _build_name_index()

    _BY_ID, _BY_NAME_ANY = _build_ability_index()

    _SPEC_LOOKUP = _build_spec_lookup()


rebuild_indices()

_EMPTY_INDEX = {KIND_AURA: ({}, {}), KIND_COOLDOWN: ({}, {})}


def match(
    abilities: SpecAbilities | None,
    name: str = "",
    spell_id: int = 0,
    prefer: str = KIND_AURA,
) -> TrackedAura | TrackedCooldown | None:
    """
    Der Eintrag einer Spezialisierung zu einem gemeldeten Namen oder
    einer Spell-ID.

    Erst die ID, dann der Name - die ID ist die einzige Angabe, die
    keine Sprache hat. `prefer` entscheidet nur bei Fähigkeiten, die
    in beiden Listen stehen; gefunden wird auch die jeweils andere.
    """

    if abilities is None:
        return None

    index = _SPEC_LOOKUP.get(
        (abilities.class_name, abilities.spec),
        _EMPTY_INDEX,
    )

    order = (
        (KIND_COOLDOWN, KIND_AURA)
        if prefer == KIND_COOLDOWN
        else (KIND_AURA, KIND_COOLDOWN)
    )

    if spell_id:

        for kind in order:

            found = index[kind][0].get(spell_id)

            if found is not None:
                return found

    key = _key(name)

    if not key:
        return None

    for kind in order:

        found = index[kind][1].get(key)

        if found is not None:
            return found

    return None


def aura_kind(name: str = "", spell_id: int = 0) -> str:
    """
    Zu welcher der drei Listen ein Effekt gehört - **spec-unabhängig**.

    Der Grund dafür, dass diese Frage überhaupt ohne Spezialisierung
    beantwortbar sein muss: eine Quelle, die alles in einen Topf legt
    (oder einen HoT unter die Buffs sortiert), würde sonst ganze
    Karten leer lassen, obwohl die Daten da sind. Ein unbekannter
    Effekt liefert einen leeren String - dann bleibt es bei der
    Einordnung der Quelle.
    """

    if spell_id:

        found = _AURA_BY_ID.get(spell_id)

        if found is not None:
            return found.kind

    found = _AURA_BY_NAME.get(_key(name))

    return found.kind if found is not None else ""


def display_name(name: str = "", spell_id: int = 0) -> str:
    """
    Der deutsche Name einer Fähigkeit, spec-unabhängig - oder der
    gemeldete Name, wenn sie unbekannt ist.

    Damit stehen in der Oberfläche nicht dieselbe Fähigkeit einmal
    englisch (weil sie aus der Raid-Cooldown-Liste kommt) und einmal
    deutsch (weil sie aus der Spec-Anreicherung kommt).
    """

    found = None

    if spell_id:
        found = _BY_ID.get(spell_id)

    if found is None:
        found = _BY_NAME_ANY.get(_key(name))

    if found is None:
        return name

    return getattr(found, "german", "") or name


def cooldown_info(
    name: str = "",
    spell_id: int = 0,
) -> TrackedCooldown | None:
    """
    Der Cooldown-Eintrag zu einem gemeldeten Namen oder einer
    Spell-ID - **spec-unabhängig**, wie `aura_kind()`.

    Der Grund, dass es diese Frage ohne Spezialisierung geben muss:
    eine Quelle meldet Cooldown-Einsätze für jeden im Raid, kennt die
    Spezialisierung des Wirkers aber nicht immer. Ohne diesen Weg
    landete ein Schildwall dann in der Schublade "geht auf
    Abklingzeit" - und der Tank bekam für jeden nicht gedrückten
    Schildwall einen verschenkten Einsatz angerechnet.
    """

    found = None

    if spell_id:
        found = _BY_ID.get(spell_id)

    if found is None:
        found = _BY_NAME_ANY.get(_key(name))

    if isinstance(found, TrackedCooldown):
        return found

    return None


def translations() -> dict[str, tuple[str, ...]]:
    """
    Englischer Name -> deutsche Schreibweisen, über alle Specs.

    Für analyzer.data.player_abilities: die Kriterien der Academy
    nennen Fähigkeiten englisch, ein deutscher Bericht liefert sie
    deutsch. Statt beide Listen von Hand gleichzuhalten, zieht die
    dortige Tabelle diese hier mit ein - eine zweite Liste würde
    driften, und das Symptom wäre eine Lektion, die dauerhaft "keine
    Daten" sagt.
    """

    table: dict[str, set[str]] = {}

    for entry in SPEC_ABILITIES:

        for ability in (*entry.auras, *entry.cooldowns):

            if not ability.english:
                continue

            for german in (ability.german, *ability.aliases):

                if german and german != ability.english:
                    table.setdefault(ability.english, set()).add(german)

    return {
        english: tuple(sorted(german))
        for english, german in table.items()
    }


def known_specs() -> tuple[tuple[str, str], ...]:
    """
    (Klasse, Spezialisierung) aller hinterlegten Einträge - für Tests
    und die Vollständigkeitsprüfung.
    """

    return tuple(
        (entry.class_name, entry.spec)
        for entry in SPEC_ABILITIES
    )
