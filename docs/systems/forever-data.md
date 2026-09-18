# Die Spieldaten von Forever — und warum sie leer sind

**Kurzfassung:** Vier Tabellen dieses Projekts haben keinen Inhalt.
Das ist kein unfertiger Stand, sondern eine Entscheidung, und dieses
Dokument hält fest, welche, warum, und woran man merkt, dass sie
wieder gefüllt werden darf.

## Was leer ist

| Tabelle | Was hineingehört |
|---|---|
| `analyzer/data/encounters.py` → `INSTANCE_ENCOUNTERS` | die Bosse je Schlachtzug, in Pull-Reihenfolge |
| `analyzer/data/encounters.py` → `DIFFICULTY_NAMES` | die `difficultyID` aus `ENCOUNTER_START` und ihr Name |
| `analyzer/data/avoidable.py` → `ENCOUNTER_ABILITIES` | welcher Bossschaden vermeidbar war |
| `analyzer/data/class_abilities.py` → `SPEC_ABILITIES` | DoTs, HoTs, Selbstbuffs und Cooldowns je Spezialisierung |
| `analyzer/data/player_abilities.py` → `ABILITY_NAMES` | englischer Fähigkeitsname → deutsche Schreibweisen |
| `analyzer/academy/lessons/classes/*.py` → `SPEC_LESSONS` | die klassenspezifischen Lektionen |
| `analyzer/academy/lessons/encounters.py` → `ENCOUNTER_LESSONS` | die bossbezogenen Lektionen |

Was **nicht** leer ist und es auch nie war:

- `analyzer/data/specs.py` — neun Klassen, je drei Talentbäume. Die
  Namen stehen seit der ersten Fassung des Spiels fest; die
  Ankündigung nennt eine Überarbeitung der Bäume, keine neuen.
- `gui/theme/wow_colors.py` — die neun Klassenfarben. Blizzard hält
  sie seit jeher konstant.
- `analyzer/data/avoidable.py` → `GLOBAL_ABILITIES` — Sturzschaden,
  Ertrinken, Erschöpfung, Nahkampfangriff. Kampfunabhängige
  Wahrheiten.
- `analyzer/academy/lessons/generic.py` und `roles.py` — Bewegung,
  Unterbrechungen, Cooldown-Disziplin, Tankwechsel. Sie gelten für
  jede Klasse und jede Spielfassung.

## Warum

Zwei Tatsachen, beide nachprüfbar:

1. **Forever überarbeitet jede Klasse und jeden Talentbaum.** Welche
   Fähigkeit danach existiert, welche Spell-ID sie trägt und wie lange
   sie abklingt, ist nicht veröffentlicht.
2. **Die Bosslisten sind nicht veröffentlicht.** Benannt sind die drei
   Schlachtzüge des Erscheinungsinhalts und ihre Gruppengrösse —
   Barrow Deeps (10), Hyjal Summit (20), Onyxias Hort (40) —, sonst
   nichts.

Die Tabellen aus Mists of Pandaria stehen zu lassen wäre der
schlimmste der drei möglichen Zustände gewesen. Sie hätten nicht
geschwiegen, sondern etwas Falsches gesagt:

> „Für Gleichgewicht werden Eclipse und Himmlische Ausrichtung
> erwartet, gemeldet wurde davon nichts."

— über einen Spieler, dessen Klasse diese Fähigkeiten gar nicht mehr
hat. Und bei den Bossmechaniken wäre daraus ein **Vorwurf** geworden:
ein Treffer, den die Tabelle als vermeidbar führt, kostet einen Stern.
Eine aus einer fremden Spielfassung übernommene Wertung erzeugt diesen
Vorwurf für jeden.

## Warum leer der richtige Zustand ist

Weil das Projekt dafür gebaut ist. Dieselbe Konvention, die überall
gilt — `stars == 0` heisst „keine Daten", nie „schlecht"; `at == -1`
heisst „kein Zeitpunkt bekannt", nie Sekunde 0 — trägt auch hier:

- `avoidable.classify()` ist **dreiwertig**. Was nicht in der Tabelle
  steht, ist `VERDICT_UNKNOWN` und nicht „unvermeidbar". Zusätzlich
  verhindert `MIN_CLASSIFIED_SHARE = 0.25`, dass über „vermeidbar"
  überhaupt etwas ausgesagt wird, solange zu wenig eingeordnet ist.
- `class_abilities.for_spec()` liefert `None` und nicht eine leere
  Hülle: „diese Spec kenne ich nicht" und „diese Spec hat nichts" sind
  verschiedene Aussagen.
- `encounters.lookup()` gibt einen `EncounterInfo` mit leerer Instanz
  zurück, und die Oberfläche zeigt den Namen aus dem Log.
- Der Lektionskatalog fällt auf `generic.py` und `roles.py` zurück —
  jeder Spieler bekommt einen sinnvollen Plan, nur keinen
  klassenspezifischen.

## Wie geprüft wird, was ohne Inhalt nicht prüfbar wäre

Ein Test, der über eine leere Tabelle läuft, wird grün, weil nichts
passiert — lautlos und wertlos. Deshalb stellen sich die Tests ihren
eigenen kleinen Bestand hin. Vier Fixtures in `tests/conftest.py`:

| Fixture | Stellt hin |
|---|---|
| `demo_abilities` | fünf Spezialisierungen mit DoT, HoT, Buff und Cooldowns in verschiedenen Schubladen, plus ihre Übersetzungen |
| `demo_lessons` | Klassen- und Bosslektionen für den Reihenfolgetest (Boss vor Spec vor Rolle vor allgemein) |
| `demo_rules` | die Bosswertung eines erfundenen Kampfes, mit beiden Urteilen |
| `demo_encounters` | denselben Kampf in Hyjal Summit, plus einen Schwierigkeitsnamen |

Geprüft wird damit der **Mechanismus** und nicht der Bestand — findet
ein deutscher Name seine Fähigkeit, bekommt ein Cooldown die richtige
Schublade, wird eine erwartete, aber nicht gemeldete Aura mit Null
ergänzt. Diese Tests bleiben gültig, egal was später in den Tabellen
steht.

Daneben stehen die **Vollständigkeitsprüfungen**, die heute nichts tun
und mit dem ersten echten Eintrag scharf werden:
`test_a_filled_table_must_cover_every_spec`,
`test_every_known_boss_has_lessons`,
`test_every_known_boss_has_reference_data`. Halb gefüllt ist der
gefährlichste Zustand — die nachgetragenen Specs bekommen
Referenzzeilen, die vergessenen sehen aus wie „die Quelle liefert
nichts".

## Die Simulation bringt ihre Wertung selbst mit

`analyzer/providers/mock.py` bildet einen erfundenen Kampf nach
(„Übungsziel") und trägt seine Bosswertung in `SIMULATED_RULES` —
nicht in den Referenzdaten. Zwei Gründe:

1. Ohne sie zeigte die Simulation null vermeidbare Treffer, und genau
   der Weg „Befund → Lektion → Sekunde im Pull" liesse sich nicht mehr
   vorführen.
2. Eine erfundene Bossmechanik gehört nicht in eine Tabelle, die
   Auskunft über das echte Spiel geben soll.

`analyzer/analysis/damage.py` nimmt dafür einen optionalen
`classifier` entgegen. Das ist die einzige Stelle, an der etwas
Erfundenes in die Auswertungskette kommt, und sie ist benannt.

## Wenn die Daten kommen

Erscheinungstermin ist der **4. November 2026**, die Schlachtzüge
öffnen am **9. Dezember**. Was dann zu tun ist:

1. Bosslisten in `INSTANCE_ENCOUNTERS` eintragen — danach greifen die
   Vollständigkeitstests für Lektionen und Referenzdaten.
2. Mechaniken in `ENCOUNTER_ABILITIES`. Nur was eindeutig ist:
   Bodenflächen, angekündigte Kegel, Zauber mit Unterbrechungsfenster,
   Tankangriffe. **Alles Strittige bleibt draussen** — eine Lücke ist
   billiger als ein falscher Vorwurf.
3. Fähigkeiten je Spec in `SPEC_ABILITIES`, in der Reihenfolge von
   `specs.py`. Die Bausteine `_dot`, `_hot`, `_buff`, `_cd` sind
   unverändert nutzbar.
4. Übersetzungen in `ABILITY_NAMES`. Die eine Tabelle, die sich
   gefahrlos früh füllen lässt: eine Übersetzung zu hinterlegen
   behauptet nicht, dass es die Fähigkeit gibt.
5. Lektionen je Spezialisierung, eine Datei je Klasse.

Jeder dieser Punkte ist eine Datenänderung in einer Datei. Kein
Umbau — das war der Zweck der Aufteilung.

## Was das für WeintCodex und den Bot heisst

Beide judgen bzw. melden dieselben Gegenstände. Sobald hier Daten
stehen, ist der Abgleich mit den Tabellen im Addon
(`analyzer/data/specs.py` ↔ Spec-Profile) und beim Bot
(`services/warcraftlogs_spells.py`) fällig — laufen sie auseinander,
ist das Symptom eine Zeile, die leer bleibt, ohne dass etwas
fehlschlägt. Siehe `docs/warcraftlogs-bridge.md`, Abschnitt „Warum die
v2-Felder leer ankamen".

## Der offene Punkt, der grösser ist als diese Tabellen

Forever läuft auf der **modernen** Client-API. Aus der Beta wird
berichtet, dass `CombatLogGetCurrentEventInfo` entfällt, dass die
Midnight-Beschränkungen gelten (eingeschränktes Kampflog, verborgene
Gegner-Lebenspunkte) und dass ein eigener Schadensmesser mitgeliefert
wird. Trifft das auf die Erscheinungsfassung zu, ist nicht nur die
*Füllung* dieser Tabellen betroffen, sondern die Frage, woher WeintTV
und die Academy ihre Zahlen überhaupt bekommen.

Das ist **kein bestätigter Stand** und stammt aus einer
Gemeinschaftsquelle, nicht von Blizzard. Es steht hier, damit es beim
Füllen der Tabellen nicht überrascht: der WarcraftLogs-Weg
(`docs/warcraftlogs-bridge.md`) ist davon vermutlich weniger betroffen
als der Weg über das Addon.
