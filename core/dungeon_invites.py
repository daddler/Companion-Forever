"""
Dungeon-Einladungen aus dem Discord ins Addon.

Der Bot meldet eine Dungeon-Einladung als Sonderraid mit `dungeon`
(`docs/raid-schedule-bridge.md`, Abschnitt *Dungeon-Einladungen*).
Während das Raid Center ruht (`RAID_FEATURES`), sind sie das Einzige
aus dem Raidtermin, das weitergeht: Forever beginnt mit Leveln, und
eine Dungeon-Runde gehört genau dahin.

Zugestellt wird über die gemeinsame Inbox (`addon/addon_inbox.py`),
Kanal `dungeons`, Nachrichtentyp `dungeon_invites`. Die Nutzlast ist
**immer** vollständig - auch ohne Einladung (`count = 0`): eine
gelöschte Einladung muss im Addon verschwinden, und ein leerer Kanal
hieße dort "nichts Neues", nicht "keine mehr".

Wie überall: Namen von Spielern stehen nicht darin, nur Zahlen - so
wie im Anmelde-Beitrag, den jeder sieht.
"""

from __future__ import annotations

from datetime import datetime, timezone

from core.raid_schedule import RaidSchedule


CHANNEL = "dungeons"

MESSAGE_TYPE = "dungeon_invites"


def build_payload(schedule: RaidSchedule | None, now: datetime | None = None) -> dict:
    """
    Alle Dungeon-Einladungen als Addon-Nutzlast. Rein, ohne Netz.

    Je Einladung der nächste Termin; vergangene fallen weg. Eine
    Einladung ohne lesbaren Termin bleibt drin (`at` fehlt) - sie
    existiert, nur ihr Zeitpunkt ist unbekannt, und das ist nicht
    "heute".
    """

    invites = []

    for entry in (schedule.all_raids() if schedule is not None else ()):

        dungeon = entry.dungeon

        if dungeon is None:
            continue

        day = entry.next_day(now)

        if day is None and entry.days:
            # Alle Termine liegen hinter uns - erledigt.
            continue

        invite = {
            "dungeon": dungeon.id,
            "name": dungeon.name,
            "title": entry.title,
            "open": entry.signup_status != "locked",
            "size": entry.raid_size or dungeon.size,
        }

        if entry.raid_id is not None:
            invite["raidId"] = entry.raid_id

        if day is not None:

            if day.starts_at is not None:
                invite["at"] = int(day.starts_at.timestamp())

            invite["active"] = day.active
            invite["tentative"] = day.tentative

            if day.me:
                invite["me"] = day.me

        invites.append(invite)

    invites.sort(key=lambda invite: invite.get("at", 2 ** 62))

    return {
        "count": len(invites),
        "invites": invites,
    }


def fingerprint(payload: dict) -> tuple:

    return tuple(
        tuple(sorted(invite.items()))
        for invite in payload.get("invites", ())
    )


class DungeonInviteSync:
    """Stellt die Dungeon-Einladungen zu, wenn sie sich geändert haben."""

    def __init__(self, manager, inbox):

        self.manager = manager

        self.inbox = inbox

        self._last = None

    def process(self, schedule: RaidSchedule | None) -> bool:

        if schedule is None:
            return False

        payload = build_payload(schedule, datetime.now(timezone.utc))
        current = fingerprint(payload)

        if current == self._last:
            return False

        delivered = self.inbox.publish(CHANNEL, [
            {"type": MESSAGE_TYPE, "payload": payload},
        ])

        if not delivered:
            return False

        self._last = current

        self.manager.logger.success(
            "Dungeon-Einladungen an das Addon übergeben: "
            f"{payload['count']}."
        )

        return True
