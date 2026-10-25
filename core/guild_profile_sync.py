"""
Berufe & Twinks an den Bot - für die Übersicht im Discord.

Meldet die Charaktere, die der Spieler in „Meine Charaktere“ verfolgt
(`CharacterStore.characters()`: diese Spielversion, nur verfolgte),
mit Stufe, Klasse, Berufen samt Fertigkeit und den Namen der bekannten
Rezepte. Der Bot zeigt das im Berufe-Channel als Dauernachricht.
Vertrag: `docs/guild-profile-bridge.md`.

Was **nicht** geht: Charaktere, die der Spieler ausgeblendet hat. Wer
seinen Bankcharakter nicht verfolgt, will ihn auch nicht im Discord
sehen - dieselbe Wahl wie beim Charakter-Roster.

`unknown ≠ 0`: eine Fertigkeit, die WeintCodex nie gelesen hat, geht
als `null`; ein Beruf, dessen Fenster nie offen war, trägt
`scanned: false` und keine Rezeptliste. Der Bot schreibt dann „?“.

Gesendet wird nur, wenn sich der Inhalt geändert hat, und gelesen nur,
wenn sich eine SavedVariables-Datei geändert hat - der Sync-Takt läuft
alle fünf Sekunden, die Berufe ändern sich beim Ausloggen.
"""

from __future__ import annotations

import hashlib
import json
import time

import httpx

from core.backend_config import BOT_BASE_URL
from core.discord_account import DiscordAccountStore


CONFIG_KEY = "profile_sync_enabled"

# Höchstens so oft wird überhaupt nachgesehen (Dateien stat-en).
CHECK_SECONDS = 120

# Und so oft nach einem Fehlschlag erneut gesendet.
RETRY_SECONDS = 600

TIMEOUT = 60


def files_stamp(wow_path) -> tuple:
    """Pfad, Änderungszeit und Größe jeder SavedVariables-Datei."""

    from core.backup import saved_variable_files

    stamp = []

    for path in saved_variable_files(wow_path):

        try:
            info = path.stat()
        except OSError:
            continue

        stamp.append((str(path), info.st_mtime_ns, info.st_size))

    return tuple(stamp)


def _label(name: str, realm: str) -> str:

    return f"{name}-{realm}" if realm else name


def build_payload(sheets: list[dict], professions, wow_client: str = "") -> dict:
    """
    Die Meldung an den Bot. Rein, ohne Dateien und Netz.

    `sheets` sind die verfolgten Charaktere (`CharacterStore.characters()`),
    `professions` das Ergebnis von `core.professions.load()`.
    """

    names: dict[int, str] = {}

    for info in getattr(professions, "catalog", {}).values():
        for spell, recipe in info.recipes.items():
            names[spell] = recipe.name

    by_label = {
        entry.label.lower(): entry
        for entry in getattr(professions, "characters", [])
    }

    characters = []

    for sheet in sheets:

        name = str(sheet.get("name") or "").strip()

        if not name:
            continue

        realm = str(sheet.get("realm") or "").strip()

        entry = by_label.get(_label(name, realm).lower()) or by_label.get(name.lower())

        rows = []

        for prof in (entry.professions if entry else []):

            row = {
                "key": prof.key,
                "name": prof.name,
                "rank": prof.rank,
                "max": prof.max,
                "scanned": bool(prof.scanned),
            }

            if prof.scanned:
                row["recipes"] = sorted(
                    {names.get(spell) or f"#{spell}" for spell in prof.known},
                    key=str.lower,
                )

            rows.append(row)

        level = sheet.get("level")

        characters.append({
            "name": name,
            "realm": realm,
            "class": str(sheet.get("class") or ""),
            "level": level if isinstance(level, int) and level > 0 else None,
            "professions": rows,
        })

    return {"wow_client": wow_client, "characters": characters}


def fingerprint(payload: dict) -> str:

    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


class GuildProfileSync:

    def __init__(self, manager):

        self.manager = manager

        self.account_store = DiscordAccountStore()

        self._stamp = None

        self._sent = None

        self._last_check = None

        self._retry_at = 0.0

    def process(self) -> bool:
        """Gibt zurück, ob eine Meldung angenommen wurde."""

        if not self.manager.config.data.get(CONFIG_KEY, True):
            return False

        account = self.account_store.load()

        if not account or not account.get("companion_token"):
            return False

        now = time.monotonic()

        if self._last_check is not None and now - self._last_check < CHECK_SECONDS:
            return False

        self._last_check = now

        wow_path = getattr(self.manager.state, "wow_path", None)

        if wow_path is None:
            return False

        store = getattr(self.manager, "characters", None)

        if store is None:
            return False

        sheets = store.characters()

        #
        # Auch die Auswahl gehört zum Stempel: wer einen Twink
        # ausblendet, ändert keine Datei des Spiels, und trotzdem soll
        # er aus dem Discord verschwinden.
        #

        stamp = files_stamp(wow_path) + tuple(store.key_of(s) for s in sheets)

        if stamp == self._stamp and self._sent is not None:
            return False

        if now < self._retry_at:
            return False

        from core import professions as core_professions

        payload = build_payload(
            sheets,
            core_professions.load(wow_path, getattr(self.manager.state, "addon_path", None)),
            self.manager.config.get_wow_client_id(),
        )

        current = fingerprint(payload)

        if current == self._sent:
            self._stamp = stamp
            return False

        try:

            response = httpx.post(
                f"{BOT_BASE_URL}/companion/profile",
                json=payload,
                headers={"Authorization": f"Bearer {account['companion_token']}"},
                timeout=TIMEOUT,
            )

        except Exception as exc:

            self.manager.logger.info(f"Berufe nicht an den Bot gemeldet: {exc}")
            self._retry_at = now + RETRY_SECONDS
            return False

        if response.status_code == 401:

            self.account_store.note_auth_rejected()
            return False

        if response.status_code == 404:

            # Ältere Bot-Fassung ohne den Endpunkt - kein Fehler.
            self._retry_at = now + RETRY_SECONDS
            return False

        if response.status_code != 200:

            self.manager.logger.info(
                f"Berufe nicht an den Bot gemeldet ({response.status_code})."
            )
            self._retry_at = now + RETRY_SECONDS
            return False

        self._sent = current
        self._stamp = stamp

        self.manager.logger.success(
            f"Berufe & Twinks an Discord gemeldet: {len(payload['characters'])} Charakter(e)."
        )

        return True
