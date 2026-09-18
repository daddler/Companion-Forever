import json
import os
from pathlib import Path

from core.paths import Paths
from core.wow_clients import (
    DEFAULT_CLIENT_ID,
    client as wow_client,
)


class Config:

    def __init__(self):

        self.file = (
            Paths.config()
            / "config.json"
        )

        self.data = {

            #
            # Welche Spielversion diese Installation bedient
            # (core/wow_clients.py). Eine unbekannte Kennung fällt dort
            # auf die Vorgabe zurück, statt den Start zu verhindern.
            #

            "wow_client": DEFAULT_CLIENT_ID,

            #
            # Der Installationspfad JE Spielversion:
            # {"forever": "..."}.
            #
            # Eine Zuordnung und nicht ein einzelner Pfad, obwohl es
            # seit 5.0 nur eine Spielversion gibt - aus demselben
            # Grund, aus dem `core/wow_clients.py` eine Tabelle mit
            # einem Eintrag ist: eine zweite kommt irgendwann wieder,
            # und dann soll der Wechsel nichts vergessen.
            #

            "wow_paths": {},

            #
            # Allgemeine Einstellungen
            #

            "check_updates": True,

            "auto_sync": True,

            "sync_interval": 5,

            "roster_sync_enabled": True,

            "character_roster_sync_enabled": True,

            #
            # Ab welcher Stufe ein Charakter in "Meine Charaktere" und
            # "Vorbereitung" erscheint: die Seiten fragen, ob man
            # raidfertig ist, und das fragt sich nur fuer Charaktere,
            # die mitkoennen. Wer seine 85er mitzaehlen will, setzt die
            # Zahl herunter.
            #
            # **0 heisst "Hoechststufe der Spielversion"** und nicht
            # "alles anzeigen" - bis 4.0 stand hier fest die 90, und
            # die waere beim Wechsel auf Forever stillschweigend falsch
            # geworden. Bestehende Installationen tragen die 90
            # weiterhin ausdruecklich; `set_wow_client()` setzt sie
            # beim Wechsel zurueck, wenn sie nie eine eigene Wahl war
            # (core/character_store.py).
            #

            "characters_min_level": 0,

            #
            # Zugriffsprofil: holt die Discord-Rollen beim Bot ab und
            # stellt dem Addon daraus Rang und Freigaben zu
            # (core/access_profile_sync.py). Ohne zugestelltes Profil
            # bleiben im Addon alle Bereiche offen.
            #

            "access_profile_sync_enabled": True,

            #
            # Zuordnung Discord-Rollenname -> Rang
            # ("gast"/"extern"/"mitglied"/"offizier"). Leer bedeutet:
            # die Standardzuordnung aus core/access_roles.py verwenden.
            # Hier eintragen, wenn Rollen im Discord anders heissen.
            #

            "access_role_map": {},

            #
            # Die Discord-Gilde, zu der das Zugriffsprofil gehoert -
            # von core/access_profile_sync.py hinterlegt, sobald der
            # Bot sie nennt. Die Uebersicht verlinkt damit auf die
            # Aufstellung. Die ID ist eine ZEICHENKETTE, nicht eine
            # Zahl: eine Discord-Snowflake sprengt die
            # Zahlengenauigkeit.
            #

            "discord_community_id": "",

            "discord_community_name": "",

            #
            # Stellt die zuletzt ausgewertete WeintTV-/Academy-Analyse
            # ins Addon (core/addon_analysis_sync.py).
            #

            "addon_analysis_sync_enabled": True,

            "start_on_boot": False,

            "minimize_to_tray": False,

            #
            # Battle.net-Start (Linux)
            #

            "linux_launcher_type": "custom",

            "linux_launcher_value": "",

            #
            # "Was ist neu"-Popup (gui/dialogs/whats_new_dialog.py)
            #

            "whats_new_enabled": True,

            "onboarding_seen_version": "",

            #
            # Fassung der Einfuehrungstour, die zuletzt gezeigt wurde.
            # Steht NEBEN onboarding_seen_version und nicht darin: nicht
            # jede Version schreibt die Tour um, und die meisten sollen
            # weiterhin nur das kurze Changelog-Popup zeigen. Wird die Tour
            # neu geschrieben, steigt die Zahl in whats_new_dialog.py -
            # und alle bekommen die Einfuehrung noch einmal.
            #

            "onboarding_tour_edition": 0,

            #
            # Module (WeintTV / WeintAcademy)
            #

            "weinttv_enabled": True,

            "academy_enabled": True,

            #
            # Seit 3.5.0 der Livelog und nicht mehr die Simulation.
            #
            # Die Simulation war der sichere Rueckfall: sie laeuft ohne
            # jede Einrichtung. Genau das war das Problem - wer die App
            # zum ersten Mal oeffnete, sah einen vollstaendigen Pull mit
            # 25 Namen, die es nicht gibt, und einen kleinen grauen Chip
            # als einzigen Hinweis darauf. "Warum steht mein Raid da
            # nicht drin" war die haeufigste Frage zu diesem Bereich.
            #
            # Ohne verknuepftes Konto oder laufenden Log steht jetzt
            # ehrlich "keine Daten" da - und die Simulation ist einen
            # Klick entfernt (die Quellenzeile auf jeder der drei
            # Seiten), statt zwei Ebenen tief in den Einstellungen.
            #

            "raid_data_source": "warcraftlogs",

            #
            # Merker der einmaligen Umstellung, siehe load(). Eine
            # frische Datei traegt ihn von Anfang an - sie startet
            # bereits auf der neuen Voreinstellung und darf nicht
            # spaeter noch einmal "umgestellt" werden.
            #

            "raid_data_source_migrated": True,

            "combatlog_path": "",

            "academy_player_name": "",

            #
            # Wer ist "ich"? Die Antwort kam bis 1.6.2 aus einer
            # Vermutung (der alphabetisch erste Raider). Seit 1.7.0
            # meldet das Addon den angemeldeten Charakter, und die
            # Auswahl folgt ihm - es sei denn, der Nutzer hat selbst
            # gewaehlt, dann gilt seine Wahl fuer genau den Charakter,
            # auf dem er sie getroffen hat (academy_manual_for).
            #
            "academy_follow_game": True,
            "academy_ingame_character": "",
            "academy_ingame_realm": "",
            "academy_player_source": "",
            "academy_manual_for": "",

            #
            # Darstellung (WeintCompanion 2.0)
            #
            # Der Akzent faerbt nur die bedeutungstragenden Stellen
            # (Navigationsindikator, Hauptknopf, Ringe, Sterne); die
            # Bedeutungsfarben bleiben in allen Varianten gleich.
            # Die Dichte gilt global, nicht pro Ansicht.
            #
            # "motion_reduced" wird zusaetzlich aus der Systemeinstellung
            # gelesen, falls Qt sie kennt - dieser Wert hier ist die
            # ausdrueckliche Wahl des Nutzers und gewinnt.
            #
            "accent": "violet",
            "density": "comfortable",
            "motion_reduced": False,
            "nav_collapsed": False,

        }

        self.load()

    # --------------------------------------------------

    def load(self):

        if not self.file.exists():

            self.save()

            return

        try:

            with open(
                self.file,
                "r",
                encoding="utf-8",
            ) as f:

                self.data.update(
                    json.load(f)
                )
                #
                # Fehlende Einstellungen ergänzen
                #

                changed = False

                defaults = {

                    "wow_client": DEFAULT_CLIENT_ID,
                    "wow_paths": {},
                    "check_updates": True,
                    "auto_sync": True,
                    "sync_interval": 5,
                    "roster_sync_enabled": True,
                    "character_roster_sync_enabled": True,
                    "characters_min_level": 0,
                    "addon_analysis_sync_enabled": True,
                    "start_on_boot": False,
                    "minimize_to_tray": False,
                    "linux_launcher_type": "custom",
                    "linux_launcher_value": "",
                    "whats_new_enabled": True,
                    "onboarding_seen_version": "",
                    "onboarding_tour_edition": 0,
                    "weinttv_enabled": True,
                    "academy_enabled": True,
                    "raid_data_source": "warcraftlogs",
                    "raid_data_source_migrated": True,
                    "combatlog_path": "",
                    "academy_player_name": "",
                    "academy_follow_game": True,
                    "academy_ingame_character": "",
                    "academy_ingame_realm": "",
                    "academy_player_source": "",
                    "academy_manual_for": "",
                    "accent": "violet",
                    "density": "comfortable",
                    "motion_reduced": False,
                    "nav_collapsed": False,

                }

                #
                # Einmalige Umstellung der Datenquelle (3.5.0).
                #
                # Der Block darunter ergaenzt nur *fehlende* Schluessel
                # - eine bestehende Installation traegt "mock" laengst
                # in ihrer Datei und bliebe damit fuer immer auf der
                # Simulation, also genau in dem Zustand, den die neue
                # Voreinstellung behebt. Die Umstellung passiert
                # deshalb genau einmal und wird vermerkt: wer die
                # Simulation danach bewusst waehlt, behaelt sie.
                #

                if not self.data.get("raid_data_source_migrated"):

                    if self.data.get("raid_data_source") == "mock":

                        self.data["raid_data_source"] = "warcraftlogs"

                    self.data["raid_data_source_migrated"] = True

                    changed = True

                for key, value in defaults.items():

                    if key not in self.data:

                        self.data[key] = value
                        changed = True

                if self._migrate_wow_paths():
                    changed = True

                if changed:

                    self.save()

        except Exception:

            #
            # Eine kaputte config.json (z. B. durch einen Absturz
            # mitten im Schreiben) wird NICHT stillschweigend mit
            # den In-Memory-Defaults überschrieben - das würde
            # sämtliche Nutzereinstellungen kommentarlos löschen.
            # Stattdessen wird die kaputte Datei beiseite gelegt,
            # damit der Verlust sichtbar/nachvollziehbar bleibt.
            #

            backup_path = self.file.with_suffix(
                self.file.suffix + ".bak"
            )

            try:

                self.file.replace(backup_path)

                print(
                    f"config.json war beschädigt und wurde nach "
                    f"{backup_path.name} verschoben - Einstellungen "
                    f"wurden auf Standardwerte zurückgesetzt."
                )

            except OSError as exc:

                print(
                    f"config.json war beschädigt und konnte nicht "
                    f"gesichert werden ({exc}) - Einstellungen werden "
                    f"auf Standardwerte zurückgesetzt."
                )

            self.save()

    # --------------------------------------------------

    def save(self):
        """
        Schreibt zuerst in eine temporäre Datei im selben Verzeichnis
        und ersetzt config.json danach atomar (os.replace) - ein
        Absturz/Stromausfall mitten im Schreiben kann so nie eine
        halbgeschriebene, kaputte config.json hinterlassen.
        """

        self.file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        tmp_path = self.file.with_suffix(
            self.file.suffix + ".tmp"
        )

        with open(
            tmp_path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                self.data,
                f,
                indent=4,
                ensure_ascii=False,
            )

        os.replace(tmp_path, self.file)

    # --------------------------------------------------
    # Spielversion
    # --------------------------------------------------

    def get_wow_client_id(self):
        """
        Die Kennung der aktiven Spielversion - **aufgelöst**, nie roh
        aus der Datei.

        Der Unterschied ist seit 5.0 ein Datenverlustrisiko. In der
        Konfiguration eines Nutzers, der von der alten Companion
        herüberkommt, steht `mop_classic`; würde diese Kennung
        unverändert durchgereicht, läse `get_wow_path()` den Ordner
        seiner MoP-Installation und diese App installierte das Addon
        in die falsche Spielversion. Die Auflösung gehört deshalb
        hierher und nicht in jeden Aufrufer: `wow_client()` kennt
        genau einen Rückfall, und den geht jeder Weg.
        """

        return wow_client(
            self.data.get("wow_client", DEFAULT_CLIENT_ID)
        ).id

    def get_wow_client(self):
        """
        Die aktive Spielversion als Eintrag aus `core/wow_clients.py`.
        Eine unbekannte Kennung fällt dort auf die Vorgabe zurück.
        """

        return wow_client(self.get_wow_client_id())

    def set_wow_client(self, client_id):
        """
        Wechselt die Spielversion.

        Nimmt dabei die Mindeststufe mit, **falls sie nie eine eigene
        Wahl war**: bis 4.0 trug jede Konfiguration die 90 aus dem
        Backfill, also die Höchststufe von MoP Classic. Wer sie nie
        angefasst hat, will nach dem Wechsel die Höchststufe der neuen
        Version und nicht die der alten - wer sie auf 85 gesetzt hat,
        behält seine 85.
        """

        previous = self.get_wow_client()

        client_id = str(client_id)

        if client_id == previous.id:
            return

        stored_minimum = self.data.get("characters_min_level")

        if (
            previous.max_level is not None
            and stored_minimum == previous.max_level
        ):

            self.data["characters_min_level"] = 0

        self.data["wow_client"] = client_id

        self.save()

    # --------------------------------------------------
    # Installationspfad (je Spielversion)
    # --------------------------------------------------

    def get_wow_path(self, client_id=None):
        """
        Der hinterlegte Ordner einer Spielversion, oder None - auch
        dann, wenn er zwar hinterlegt ist, aber nicht mehr existiert
        (externe Platte abgezogen, Neuinstallation woanders).
        """

        client_id = client_id or self.get_wow_client_id()

        paths = self.data.get("wow_paths")

        if not isinstance(paths, dict):
            paths = {}

        path = paths.get(client_id, "")

        if not path:
            return None

        path = Path(path)

        if path.exists():
            return path

        return None

    # --------------------------------------------------

    def set_wow_path(self, path, client_id=None):

        client_id = client_id or self.get_wow_client_id()

        paths = self.data.get("wow_paths")

        if not isinstance(paths, dict):
            paths = {}

        paths[client_id] = str(path)

        self.data["wow_paths"] = paths

        self.save()

    # --------------------------------------------------

    def _migrate_wow_paths(self) -> bool:
        """
        Sorgt dafür, dass `wow_paths` eine Zuordnung ist.

        Läuft bei jedem Laden und nicht einmalig mit Merker: sie ist
        idempotent, weil sie nur einen *fehlenden* Wert ergänzt - ein
        Merker wäre hier ein zweiter Zustand, der falsch stehen kann,
        für eine Ersparnis von einem Wörterbuchzugriff.

        WAS SIE ABSICHTLICH NICHT TUT
        -----------------------------

        Die Konfiguration eines Nutzers, der von der alten Companion
        herüberkommt, enthält `classic_path` und
        `wow_paths["mop_classic"]` - den Ordner seiner
        MoP-Installation. Der wird **nicht** als Forever-Pfad
        übernommen. Das ist der Unterschied zwischen "der Nutzer muss
        seinen Ordner einmal wählen" und "die App installiert das
        Addon in die falsche Spielversion", und nur eines davon lässt
        sich rückgängig machen.

        Gelöscht werden die beiden Schlüssel ebenso wenig: sie stehen
        in derselben Datei, die eine ältere Companion-Fassung liest,
        falls jemand zurückgeht. Sie kosten zwei Zeilen und ersparen
        ihm die Suche.
        """

        if isinstance(self.data.get("wow_paths"), dict):
            return False

        self.data["wow_paths"] = {}

        return True

    # --------------------------------------------------
    # Battle.net-Start (Linux)
    # --------------------------------------------------

    def get_linux_launcher_type(self):

        return self.data.get(
            "linux_launcher_type",
            "custom",
        )

    def get_linux_launcher_value(self):

        return self.data.get(
            "linux_launcher_value",
            "",
        )

    def set_linux_launcher(self, launcher_type, value):

        self.data["linux_launcher_type"] = launcher_type
        self.data["linux_launcher_value"] = value.strip()

        self.save()

    def get_linux_launch_command(self):
        """
        Baut aus Launcher-Typ + Wert den tatsächlich auszuführenden
        Befehl. "lutris"/"steam"/"faugus" kennen eine feste
        CLI-Syntax, bei "custom" (z. B. Bottles, Heroic, ...) ist
        der Wert bereits der vollständige Befehl.
        """

        launcher_type = self.get_linux_launcher_type()
        value = self.get_linux_launcher_value()

        if not value:
            return ""

        if launcher_type == "lutris":
            return f"lutris lutris:rungame/{value}"

        if launcher_type == "steam":
            return f"steam steam://rungameid/{value}"

        if launcher_type == "faugus":
            return f"faugus-launcher --game {value}"

        return value