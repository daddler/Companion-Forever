"""
Fehlerberichte an den Bot (seit 1.0.5, Addon ab 1.0.5.28).

Im Spiel klickt der Spieler im Fehlerfenster „Melden & neu laden“: das
Addon merkt den Fehler vor (`errors[i].report = "pending"`) und lädt neu,
damit er in der Datei steht. Diese Klasse findet solche Fehler und
schickt jeden genau einmal an den Bot (`POST /companion/bug-report`); der
legt einen Beitrag im Forum an. Dazu `send()` für den Knopf auf der Seite
„Addon-Fehler“.

Gesendet heißt: der Bot hat "ok" gesagt. Erst dann landet der Schlüssel
in der Konfiguration (`bug_reports_sent`) - ein Fehlschlag wird später
erneut versucht, ein gesendeter nie zweimal.

Vertrag: docs/bug-report-bridge.md
"""

from __future__ import annotations

import time

import httpx

from core.backend_config import BOT_BASE_URL
from core.discord_account import DiscordAccountStore
from core.version import VERSION

SENT_KEY = "bug_reports_sent"
SENT_MAX = 200
CHECK_SECONDS = 15
RETRY_SECONDS = 120
TIMEOUT = 40


def payload(error) -> dict:

    return {
        "kind": error.kind,
        "message": error.message,
        "stack": error.stack,
        "count": error.count,
        "first": error.first,
        "last": error.last,
        "addon_version": error.version,
        "client": error.client,
        "locale": error.locale,
        "class": error.wow_class,
        "level": error.level,
        "zone": error.zone,
        "character": error.account,
        "companion_version": VERSION,
    }


class BugReportSync:

    def __init__(self, manager):

        self.manager = manager
        self.account_store = DiscordAccountStore()
        self._stamp = None
        self._last_check = None
        self._retry_at = 0.0

    # --------------------------------------------------

    def _sent(self) -> list:

        sent = self.manager.config.data.get(SENT_KEY)
        return sent if isinstance(sent, list) else []

    def _mark_sent(self, key: str):

        sent = [k for k in self._sent() if k != key] + [key]
        self.manager.config.data[SENT_KEY] = sent[-SENT_MAX:]
        try:
            self.manager.config.save()
        except Exception as exc:
            self.manager.logger.info(f"Gesendete Fehlerberichte nicht gespeichert: {exc}")

    def is_sent(self, error) -> bool:

        return error.report_key in self._sent()

    # --------------------------------------------------

    def send(self, error) -> tuple[bool, str]:
        """Einen Fehler senden. (gesendet?, Satz für den Spieler)"""

        account = self.account_store.load()

        if not account or not account.get("companion_token"):
            return False, "Melde dich zuerst mit Discord an (Einstellungen → Discord)."

        try:
            response = httpx.post(
                f"{BOT_BASE_URL}/companion/bug-report",
                json=payload(error),
                headers={"Authorization": f"Bearer {account['companion_token']}"},
                timeout=TIMEOUT,
            )
        except Exception as exc:
            return False, f"Der Bot ist gerade nicht erreichbar ({type(exc).__name__}). Später erneut versuchen."

        if response.status_code == 401:
            self.account_store.note_auth_rejected()
            return False, "Die Discord-Anmeldung ist abgelaufen. Bitte neu verbinden."

        if response.status_code == 404:
            return False, "Der Bot kennt Fehlerberichte noch nicht. Später erneut versuchen."

        if response.status_code != 200:
            return False, f"Der Bot hat den Bericht nicht angenommen ({response.status_code})."

        self._mark_sent(error.report_key)
        return True, "Danke! Der Fehler ist beim Entwickler angekommen."

    # --------------------------------------------------

    def process(self) -> int:
        """Vorgemerkte Fehler senden. Gibt die Zahl der gesendeten zurück."""

        now = time.monotonic()

        if self._last_check is not None and now - self._last_check < CHECK_SECONDS:
            return 0

        self._last_check = now

        if now < self._retry_at:
            return 0

        wow_path = getattr(self.manager.state, "wow_path", None)

        if wow_path is None:
            return 0

        from core.guild_profile_sync import files_stamp

        stamp = files_stamp(wow_path)

        if stamp == self._stamp:
            return 0

        from core import addon_errors

        found = addon_errors.load(wow_path)
        sent = 0
        failed = False

        for error in found.errors:

            if error.report != "pending" or self.is_sent(error):
                continue

            ok, text = self.send(error)

            if ok:
                sent += 1
                self.manager.logger.success(f"Fehlerbericht an Discord geschickt: {error.headline[:80]}")
            else:
                failed = True
                self.manager.logger.info(f"Fehlerbericht nicht gesendet: {text}")
                break

        if failed:
            self._retry_at = now + RETRY_SECONDS
        else:
            self._stamp = stamp

        return sent
