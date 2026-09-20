"""
Die Charakterliste der Anwendung.

Das Addon meldet immer nur **einen** Charakter: den gerade
angemeldeten (`"character_sheet"`, siehe
`core/character_sheet_sync.py`). Die Liste über mehrere Twinks
entsteht deshalb hier - sie ist die einzige Stelle, an der die
Meldungen mehrerer Anmeldungen zusammenkommen.

Das ist kein Zwischenspeicher, sondern die Datenquelle zweier Seiten,
und sie liegt entsprechend in `Paths.config()`: Wer seit zwei Wochen
nicht auf dem Zweitcharakter war, soll ihn in "Meine Charaktere"
trotzdem sehen. In `Paths.cache()` wäre er beim ersten Aufräumen weg,
und die Seite behauptete, es gäbe ihn nicht.

Vier Regeln, die nicht nach Geschmack sind:

* **Eine neue Meldung ersetzt den Eintrag, sie ergänzt ihn nicht.**
  Ein Feld, das die neue Meldung nicht mehr trägt, ist keine
  Erinnerung wert: es beschriebe einen Zustand, den es nicht mehr
  gibt. Wer eine Verzauberung entfernt, soll sie nicht deshalb weiter
  als vorhanden angezeigt bekommen, weil die vorige Meldung sie noch
  kannte.
* **Nur der Zeitstempel entscheidet über die Reihenfolge**, nicht die
  Reihenfolge der Verarbeitung. Sonst hinge "zuletzt gespielt" daran,
  wann die App lief.
* **Gezeigt werden nur Charaktere ab der eingestellten Stufe**, siehe
  `min_level()` weiter unten. Twinks bleiben gespeichert - sie werden
  nur nicht ausgegeben, und `all_characters()` liefert sie weiterhin.
  Wegwerfen wäre das Falsche: wer einen Twink hochspielt, soll ihn am
  Tag der Höchststufe mit seiner Vorgeschichte wiederfinden und nicht
  als Neuzugang. Für Forever steht die Grenze bei 1 - siehe
  `character_min_level` in `core/wow_clients.py`.
* **Jeder Eintrag trägt die Spielversion, die ihn gemeldet hat**, und
  gezeigt wird nur die aktive. Diese Liste liegt seit jeher unter
  `~/.local/share/WeintCompanion` bzw. `%LOCALAPPDATA%/WeintCompanion`
  - demselben Ordner, den die **alte** Companion für Mists of Pandaria
  benutzt. Wer herüberkommt, bringt seine MoP-Charaktere also mit, und
  ohne diesen Vermerk stünden sie hier als Forever-Charaktere: Stufe
  90 in einem Spiel, das bei 60 endet, mit einer Ausrüstung, die es
  dort nicht gibt. Gelöscht werden sie deshalb trotzdem nicht - sie
  sind die Vorgeschichte eines Nutzers und gehören ihm, nicht dieser
  App.
"""

from __future__ import annotations

import json
import os
import time

from core.character_sheet_sync import (
    parse_character_sheet,
    readiness,
    sheet_key,
)
from core.paths import Paths
from core.wow_clients import (
    client as wow_client,
    client_label,
    is_known_client,
)


CHARACTERS_FILE = "characters.json"


#
# Der Vermerk im Eintrag: welche Spielversion diesen Charakter
# gemeldet hat. Er steht im Datensatz und nicht in einem zweiten
# Verzeichnis daneben, weil er zum Charakter gehört und nicht zur
# Datei - wer die Liste kopiert, kopiert ihn mit.
#

CLIENT_KEY = "wow_client"


#
# Die Kennung für "eine frühere Spielversion, die sich nicht mehr
# benennen lässt". Sie ist keine Spielversion und steht deshalb auch
# in keiner Tabelle: `client_label()` gibt für sie den leeren Text,
# und die Oberfläche sagt dann "eine frühere Spielversion", statt
# einen Namen zu erfinden.
#

UNKNOWN_CLIENT = "?"


#
# Ab welcher Stufe ein Charakter in "Meine Charaktere" und
# "Vorbereitung" auftaucht.
#
# Beide Seiten beantworten dieselbe Frage - "kann ich damit in den
# Raid" -, und die stellt sich nur für Charaktere, die mitkommen
# können. Bis 2.3.0 bekam jede Anmeldung eine Karte: wer nebenher
# vier Twinks hochspielt, fand die eine Höchststufe, um die es geht,
# zwischen vier Zeilen, die nichts mit dem nächsten Raidabend zu tun
# haben.
#
# Seit 4.1 kommt die Zahl aus der Spielversion
# (`core/wow_clients.py`) und steht nicht mehr fest hier; seit 5.0.3
# ist es dort nicht mehr zwingend die Höchststufe, weil ein frisch
# erschienenes Spiel keine hat. `characters_min_level` in der
# Konfiguration setzt den Wert je Installation - dieselbe Überlegung
# wie bei `access_role_map`: eine Zahl, die sich mit dem Spiel ändert,
# soll ohne ein Release änderbar bleiben.
#
# Die Konstanten hier bleiben der Rückfall für `is_high_level()`, wenn
# niemand eine Mindeststufe mitgibt - also für die reine Funktion
# ohne Ablage und ohne Konfiguration.
#

MAX_LEVEL = 60

MIN_LEVEL = MAX_LEVEL


def default_min_level(client_id=None) -> int:
    """
    Die Mindeststufe, solange niemand eine eigene eingetragen hat.

    Sie kommt aus der Spielversion und ist für Forever die **1**: ein
    frisch erschienenes Spiel hat wochenlang niemanden auf
    Höchststufe, und eine Liste, die erst ab 60 etwas zeigt, wäre
    genau in dieser Zeit leer. Die Begründung steht bei
    `character_min_level` in `core/wow_clients.py` - dort, wo sie sich
    mit der nächsten Spielversion wieder ändern kann.

    **Ist die Höchststufe unbekannt, wird 1 zurückgegeben und nicht
    die Zahl einer anderen Spielversion.** Eine geratene Höchststufe
    liesse Charaktere aus "Meine Charaktere" verschwinden, über deren
    Stufe nichts bekannt ist - dieselbe Linie wie `is_high_level()`
    selbst, wo eine fehlende Stufe als hohe zählt: aus einer
    Datenlücke wird kein Befund.
    """

    target = wow_client(client_id)

    if target.character_min_level is not None:
        return max(1, target.character_min_level)

    return target.max_level or 1


def sheet_client(sheet: dict) -> str:
    """
    Die Spielversion, die einen Eintrag gemeldet hat - leer, solange
    keine vermerkt ist.
    """

    return str(sheet.get(CLIENT_KEY) or "").strip()


def archive_key(key: str, origin: str) -> str:
    """
    Der Ablageschlüssel eines Charakters, der **nicht** zur laufenden
    Spielversion gehört.

    Er trägt die Herkunft vorn, damit ein gleichnamiger Charakter aus
    zwei Spielen zwei Einträge bleibt. Gelesen wird er über keinen
    anderen Weg als `all_characters()` - der Schlüssel ist eine
    Ablage, keine Kennung.
    """

    return f"{origin or UNKNOWN_CLIENT}:{key}"


def belongs_to(sheet: dict, client_id: str) -> bool:
    """
    Gehört der Eintrag zur laufenden Spielversion?

    **Ohne Vermerk: ja.** Die Einträge ohne Vermerk sind beim Laden
    einmalig zugeordnet worden (`CharacterStore.adopt_untagged()`);
    was danach noch ohne dasteht, ist eine Datenlücke - und aus einer
    Datenlücke wird in diesem Projekt kein Befund, schon gar keiner,
    der einen Charakter verschwinden lässt.
    """

    origin = sheet_client(sheet)

    return not origin or origin == client_id


def is_high_level(sheet: dict, minimum: int = MIN_LEVEL) -> bool:
    """
    **Eine fehlende Stufe zählt als hohe.**

    Die 0 steht hier für "nicht gemeldet" und nicht für "Stufe 0" -
    eine ältere Addon-Version, ein abgeschnittenes Feld, ein Eintrag
    aus einer Zeit vor diesem Feld. Wer sie als Twink läse, ließe
    einen Charakter verschwinden, über den nichts bekannt ist; das ist
    dieselbe Linie wie `stars == 0` und `readiness() is None`: aus
    einer Datenlücke wird kein Befund.
    """

    try:
        level = int(sheet.get("level") or 0)

    except (TypeError, ValueError):
        return True

    if level <= 0:
        return True

    return level >= minimum


class CharacterStore:

    def __init__(self, manager):

        self.manager = manager

        self.file = Paths.config() / CHARACTERS_FILE

        #
        # Aufbau: {"<Name-Realm>": <Sheet>, ...}
        #
        # Der Schlüssel trägt den Realm, weil zwei Realms denselben
        # Namen führen dürfen - ohne ihn überschriebe der eine
        # Charakter die Ausrüstung des anderen.
        #

        self.data: dict = {}

        self.load()

    # --------------------------------------------------
    # Persistenz
    # --------------------------------------------------

    def load(self):

        if not self.file.exists():
            return

        try:

            with open(self.file, "r", encoding="utf-8") as handle:

                loaded = json.load(handle)

            if isinstance(loaded, dict):

                self.data = {
                    str(key): value
                    for key, value in loaded.items()
                    if isinstance(value, dict) and value.get("name")
                }

        except Exception as exc:

            #
            # Eine defekte Liste darf die Anwendung nicht aufhalten -
            # sie füllt sich bei der nächsten Anmeldung im Spiel von
            # selbst wieder.
            #

            self.manager.logger.warning(
                f"Charakterliste konnte nicht gelesen werden ({exc}) - "
                f"sie wird beim nächsten Anmelden im Spiel neu "
                f"aufgebaut."
            )

            self.data = {}

            return

        self.adopt_untagged()

    def save(self):
        """
        Atomar schreiben - dasselbe Vorgehen wie in `core/config.py`
        und `core/academy_service.py`, damit ein Absturz mitten im
        Schreiben keine halbe Datei hinterlässt.
        """

        try:

            self.file.parent.mkdir(parents=True, exist_ok=True)

            tmp_path = self.file.with_suffix(self.file.suffix + ".tmp")

            with open(tmp_path, "w", encoding="utf-8") as handle:

                json.dump(
                    self.data,
                    handle,
                    indent=4,
                    ensure_ascii=False,
                )

            os.replace(tmp_path, self.file)

        except OSError as exc:

            self.manager.logger.error(
                f"Charakterliste konnte nicht gespeichert werden: {exc}"
            )

    # --------------------------------------------------
    # Spielversion
    # --------------------------------------------------

    def _config_data(self) -> dict:

        config = getattr(self.manager, "config", None)

        return getattr(config, "data", None) or {}

    def client_id(self) -> str:
        """
        Die Kennung der laufenden Spielversion - **aufgelöst**, nie roh
        aus der Datei. `Config.get_wow_client_id()` erklärt, warum
        (kurz: in einer mitgebrachten Konfiguration steht noch
        `mop_classic`).
        """

        config = getattr(self.manager, "config", None)

        resolve = getattr(config, "get_wow_client_id", None)

        if callable(resolve):

            try:
                return resolve()

            except Exception:
                pass

        return wow_client(self._config_data().get("wow_client")).id

    def _origin_of_untagged(self) -> str:
        """
        Welche Spielversion die Einträge **ohne** Vermerk gemeldet hat.

        Es gibt sie nur einmal: in der Liste, die eine Fassung vor
        5.0.3 geschrieben hat. Die Frage ist dann, ob diese Fassung
        die alte Companion für Mists of Pandaria war oder eine frühe
        Forever-Fassung - und die Antwort steht in der Konfiguration,
        die im selben Ordner liegt:

        * Eine Kennung, die diese App nicht kennt (`mop_classic`), ist
          die Konfiguration der alten Companion. Sie wird nirgends
          überschrieben (siehe `Config.get_wow_client_id()`), ist also
          noch da, wenn diese Frage gestellt wird.
        * Eine Mindeststufe **über** der Höchststufe dieser
          Spielversion (die 90 aus MoP) kann keine Wahl für Forever
          sein. Wer sie trägt, hat die alte Companion benutzt, auch
          wenn seine Kennung inzwischen umgeschrieben wurde.

        Trifft keines von beidem zu, gehört die Liste dieser
        Spielversion. Das ist die vorsichtige Antwort: sie zeigt im
        Zweifel einen Charakter zu viel statt einen zu wenig.
        """

        data = self._config_data()

        stored = str(data.get("wow_client") or "").strip()

        if stored and not is_known_client(stored):
            return stored

        active = self.client_id()

        cap = wow_client(active).max_level

        minimum = data.get("characters_min_level")

        if (
            cap
            and isinstance(minimum, int)
            and not isinstance(minimum, bool)
            and minimum > cap
        ):
            return UNKNOWN_CLIENT

        return active

    def adopt_untagged(self):
        """
        Trägt die Spielversion in die Einträge nach, die noch keine
        haben - einmalig, beim ersten Laden mit dieser Fassung.

        Danach steht sie **in der Datei**. Das ist der ganze Zweck:
        die Spur, aus der sich die Herkunft ablesen lässt (die alte
        Konfiguration), verschwindet, sobald der Nutzer die
        Spielversion einmal in den Einstellungen anfasst. Wer die
        Frage bei jeder Anzeige neu stellte, bekäme irgendwann eine
        andere Antwort, und die MoP-Charaktere stünden wieder da.
        """

        untagged = [
            sheet
            for sheet in self.data.values()
            if not sheet_client(sheet)
        ]

        if not untagged:
            return

        active = self.client_id()

        origin = self._origin_of_untagged()

        cap = wow_client(active).max_level

        for sheet in untagged:

            if origin != active:

                #
                # Die Konfiguration hat die Frage beantwortet, und
                # zwar mit einem Namen. Der gilt dann für die ganze
                # Liste - sie ist in einem Stück von dort
                # herübergekommen.
                #

                sheet[CLIENT_KEY] = origin

                continue

            #
            # Sonst entscheidet der Eintrag selbst: eine Stufe über
            # der Höchststufe dieser Spielversion kann nicht aus ihr
            # stammen - in einem Spiel, das bei 60 endet, gibt es
            # keine 90. Woher sie stammt, ist damit aber nicht gesagt.
            #

            try:
                level = int(sheet.get("level") or 0)

            except (TypeError, ValueError):
                level = 0

            sheet[CLIENT_KEY] = (
                UNKNOWN_CLIENT
                if cap and level > cap
                else active
            )

        self.save()

    # --------------------------------------------------
    # Aufnehmen
    # --------------------------------------------------

    def apply(self, payload: str) -> dict | None:
        """
        Eine `character_sheet`-Nutzlast aufnehmen. Gibt den zerlegten
        Eintrag zurück, damit der Aufrufer ihn protokollieren kann,
        oder `None`, wenn nichts anzuwenden war.
        """

        sheet = parse_character_sheet(payload)

        if sheet is None:
            return None

        key = sheet_key(sheet["name"], sheet["realm"])

        if not key:
            return None

        #
        # Ein Addon ohne verlässliche Uhr (oder ein Format, das das
        # Feld noch nicht trägt) bekommt den Empfangszeitpunkt. Ohne
        # Zeitstempel wäre die Sortierung "zuletzt gespielt" beliebig.
        #

        if not sheet.get("updated"):
            sheet["updated"] = int(time.time())

        #
        # Die Meldung kommt aus der SavedVariables-Datei der
        # eingerichteten Installation - also aus der Spielversion, die
        # gerade eingestellt ist. Der Vermerk wird deshalb hier gesetzt
        # und nicht vom Addon erfragt: das Addon weiss, wer sich
        # angemeldet hat, aber nicht, in welchem Ordner es liegt.
        #

        sheet[CLIENT_KEY] = self.client_id()

        #
        # Steht unter diesem Schlüssel ein Charakter einer **anderen**
        # Spielversion, wird er beiseitegelegt und nicht überschrieben.
        # Name und Realm dürfen sich zwischen zwei Spielen wiederholen
        # - wer in Forever wieder "Njiah" auf "Everlook" spielt, würde
        # sonst seinen MoP-Eintrag genau in dem Augenblick verlieren,
        # in dem er ihn am ehesten wiedersehen will. "Ersetzen statt
        # ergänzen" gilt für Meldungen desselben Charakters, nicht für
        # zwei gleichnamige aus zwei Spielen.
        #

        previous = self.data.get(key)

        if previous is not None and not belongs_to(previous, sheet[CLIENT_KEY]):

            self.data[archive_key(key, sheet_client(previous))] = previous

        self.data[key] = sheet

        self.save()

        return sheet

    # --------------------------------------------------
    # Lesen
    # --------------------------------------------------

    def min_level(self) -> int:
        """
        Die eingestellte Mindeststufe. Ein unbrauchbarer Wert wird
        **ignoriert und nicht übernommen** - eine 0 in der
        Konfiguration hiesse sonst "alles anzeigen", und eine 200
        "nichts anzeigen"; beides sieht aus wie eine kaputte Seite.

        Unbrauchbar ist seit 5.0.3 auch eine Zahl **über** der
        Höchststufe dieser Spielversion, und das ist kein Randfall:
        jede Konfiguration, die von der alten Companion herüberkommt,
        trägt die 90 von Mists of Pandaria. In einem Spiel, das bei 60
        endet, erreicht sie niemand - die Seite bliebe für immer leer,
        und zwar ohne jeden Hinweis darauf, warum.

        Die Zahl wird dabei **nicht** in der Datei berichtigt. Sie
        steht dort wie `classic_path` als Spur der alten Fassung: wer
        zurückgeht, findet seine Einstellung wieder, und wer bleibt,
        merkt nichts davon.
        """

        data = self._config_data()

        fallback = default_min_level(data.get("wow_client"))

        value = data.get("characters_min_level")

        try:
            minimum = int(value)

        except (TypeError, ValueError):
            return fallback

        if minimum < 1:
            return fallback

        cap = wow_client(data.get("wow_client")).max_level

        if cap and minimum > cap:
            return fallback

        return minimum

    def all_characters(self) -> list[dict]:
        """
        Alle bekannten Charaktere, zuletzt gespielter zuerst -
        einschliesslich der Twinks.
        """

        return sorted(
            self.data.values(),
            key=lambda sheet: sheet.get("updated", 0),
            reverse=True,
        )

    def own_characters(self) -> list[dict]:
        """
        Alle Charaktere **dieser** Spielversion - auch die Twinks.
        """

        active = self.client_id()

        return [
            sheet
            for sheet in self.all_characters()
            if belongs_to(sheet, active)
        ]

    def characters(self) -> list[dict]:
        """
        Die Charaktere, die die Seiten zeigen: diese Spielversion, ab
        der eingestellten Stufe, zuletzt gespielter zuerst.
        """

        minimum = self.min_level()

        return [
            sheet
            for sheet in self.own_characters()
            if is_high_level(sheet, minimum)
        ]

    def hidden(self) -> list[dict]:
        """
        Die ausgeblendeten Twinks.

        Sie werden gebraucht, um das Ausblenden **zu benennen**: ein
        Charakter, der aus einer Liste verschwindet, in der er gestern
        noch stand, ist sonst nicht von einem Fehler zu unterscheiden.
        """

        minimum = self.min_level()

        return [
            sheet
            for sheet in self.own_characters()
            if not is_high_level(sheet, minimum)
        ]

    def foreign(self) -> list[dict]:
        """
        Die Charaktere aus einer anderen Spielversion - in aller Regel
        die MoP-Charaktere eines Nutzers, der von der alten Companion
        herüberkommt.

        Dieselbe Aufgabe wie `hidden()`: sie werden gebraucht, um ihr
        Fehlen zu benennen. Wer seine sechs Charaktere gewohnt ist und
        nach dem Umstieg eine leere Seite sieht, hält das für einen
        Fehler der App - und liegt damit nicht einmal falsch, wenn
        niemand es ihm sagt.
        """

        active = self.client_id()

        return [
            sheet
            for sheet in self.all_characters()
            if not belongs_to(sheet, active)
        ]

    def foreign_label(self) -> str:
        """
        Der Name der Spielversion, aus der die fremden Charaktere
        stammen - leer, wenn es keine gibt, mehrere sind oder die
        Kennung nichts mehr sagt. Die Oberfläche sagt dann "eine
        frühere Spielversion".
        """

        origins = {
            sheet_client(sheet)
            for sheet in self.foreign()
        }

        if len(origins) != 1:
            return ""

        return client_label(origins.pop())

    def get(self, name: str, realm: str = "") -> dict | None:

        key = sheet_key(name, realm)

        if key in self.data:
            return self.data[key]

        #
        # Ohne Realm gesucht: der blanke Name darf den qualifizierten
        # Eintrag finden. Der Client kennt nur den nackten Namen -
        # dieselbe Regel wie in `analyzer/names.py`, wo ein fehlender
        # Realm ein Platzhalter ist und kein Widerspruch.
        #

        if not realm:

            bare = (name or "").strip().lower()

            #
            # Über `all_characters()`, nicht über `characters()`: die
            # Ausblendung gilt der Anzeige. Ein Twink, der gerade eine
            # Ausrüstung meldet, muss auch gefunden werden - sonst
            # legte `apply()` bei jeder Anmeldung einen zweiten
            # Eintrag an.
            #
            # **Diese Spielversion zuerst.** Ein blanker Name kann
            # zweimal vorkommen, seit die Liste auch die Charaktere
            # eines anderen Spiels trägt; gemeint ist dann der, den
            # man gerade spielt, und nicht der aus dem alten Spiel.
            #

            for sheets in (self.own_characters(), self.all_characters()):

                for sheet in sheets:

                    if sheet.get("name", "").strip().lower() == bare:
                        return sheet

        return None

    def remove(self, name: str, realm: str = "") -> bool:

        key = sheet_key(name, realm)

        if key not in self.data:

            found = self.get(name, realm)

            if found is None:
                return False

            key = sheet_key(found.get("name", ""), found.get("realm", ""))

        if key not in self.data:
            return False

        del self.data[key]

        self.save()

        return True

    # --------------------------------------------------
    # Zusammenfassung für die Übersicht
    # --------------------------------------------------

    def preparation_summary(self) -> dict:
        """
        Der Stand der Vorbereitung über alle gemeldeten Charaktere.

        `ratio` ist `None`, solange kein einziger Charakter geprüfte
        Verzauberungen oder Sockel gemeldet hat. Eine Null stünde dort
        für "alles offen" und wäre eine Messung, die es nicht gab -
        dieselbe Trennung wie `stars == 0` im Analyzer.

        Gezählt wird über `characters()`, also **ohne die Twinks**:
        die Kachel auf der Übersicht und die Seite "Vorbereitung"
        lesen dieselbe Zusammenfassung und dürfen sich nicht darin
        unterscheiden, wen sie meinen. Eine fehlende Verzauberung auf
        einem Charakter der Stufe 34 ist ausserdem keine offene
        Stelle, sondern der Normalfall.
        """

        sheets = self.characters()

        ratios = []

        open_count = 0

        for sheet in sheets:

            ratio = readiness(sheet)

            if ratio is None:
                continue

            ratios.append(ratio)

            for counts in (sheet.get("enchants"), sheet.get("gems")):

                if counts:
                    open_count += counts.get("missing", 0)

        return {
            "characters": len(sheets),
            "rated": len(ratios),
            "ratio": (sum(ratios) / len(ratios)) if ratios else None,
            "open": open_count,
            "hidden": len(self.hidden()),
            "foreign": len(self.foreign()),
        }
