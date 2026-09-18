from dataclasses import dataclass
from pathlib import Path

from core.version import VERSION
from core.wow_clients import DEFAULT_CLIENT_ID


@dataclass
class AppState:

    # --------------------------------------------------
    # World of Warcraft
    # --------------------------------------------------

    #
    # Welche Spielversion gerade bedient wird
    # (core/wow_clients.py). Steht hier und nicht nur in der
    # Konfiguration, damit die Oberfläche sie beim Zeichnen zur Hand
    # hat, ohne dafür die Konfiguration zu befragen - eine Seite darf
    # in `refresh()` nichts holen (docs/architecture/navigation.md).
    #

    wow_client_id: str = DEFAULT_CLIENT_ID

    wow_found: bool = False

    wow_path: Path | None = None

    addons_path: Path | None = None

    # --------------------------------------------------
    # Addon
    # --------------------------------------------------

    addon_found: bool = False

    addon_path: Path | None = None

    addon_version: str = "-"

    # --------------------------------------------------
    # GitHub (Addon)
    # --------------------------------------------------

    github_version: str = "-"

    github_release_name: str = ""

    github_changelog: str = ""

    github_download_url: str = ""

    github_asset_name: str = ""

    github_published: str = ""

    github_sha256: str = ""

    # --------------------------------------------------
    # Addon Update
    # --------------------------------------------------

    update_available: bool = False

    # --------------------------------------------------
    # Companion
    # --------------------------------------------------

    companion_version: str = VERSION

    companion_latest_version: str = VERSION

    companion_download_url: str = ""

    companion_asset_name: str = ""

    companion_sha256: str = ""

    companion_update_available: bool = False

    companion_changelog: list[str] | None = None

    # --------------------------------------------------
    # Discord Bot
    # --------------------------------------------------

    discord_connected: bool = False

    discord_name: str = "-"

    discord_guilds: int = 0

    discord_latency: int | None = None

    # --------------------------------------------------
    # Wann zuletzt etwas passiert ist
    # --------------------------------------------------
    #
    # Zwei Zeitpunkte als Epochensekunden, oder `0.0` für "noch nie".
    #
    # Die Null ist hier **keine** Uhrzeit, sondern eine Datenlücke -
    # dieselbe Unterscheidung wie `at == -1` im Analyzer. Die
    # Oberfläche schreibt dafür "noch nicht geprüft" und nicht
    # "01.01.1970"; wer sie als Zeitpunkt läse, bekäme die härteste
    # denkbare Untertreibung.
    #
    # Sie stehen hier und nicht in der Konfiguration: sie überleben
    # den Programmlauf nicht und sollen es auch nicht. "Zuletzt
    # geprüft vor drei Minuten" meint diese Sitzung; was vor dem
    # letzten Start war, beantwortet das Protokoll.
    #

    last_check_at: float = 0.0

    last_sync_at: float = 0.0