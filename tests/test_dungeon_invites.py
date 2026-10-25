"""
Dungeon-Einladungen: vom Termin-Endpunkt ins Addon.

Geprüft wird die reine Rechnung (`build_payload`) und dass die
Zustellung nur bei Änderung schreibt - ohne Netz, ohne Qt.
"""

from datetime import datetime, timezone

from core.dungeon_invites import DungeonInviteSync, build_payload
from core.raid_schedule import parse_schedule


NOW = datetime(2026, 8, 11, 12, 0, tzinfo=timezone.utc)


def _day(key, starts_at, active=0):
    return {
        "key": key,
        "label": key,
        "starts_at": starts_at,
        "signups": {"active": active, "tentative": 1, "bench": 0, "absent": 0},
        "me": "active",
    }


RAID = {
    "status": "ok",
    "raid_id": 7,
    "title": "Raid",
    "raid_type": "standard",
    "raid_size": 25,
    "days": [_day("wednesday", "2026-08-12T20:00:00+02:00", 18)],
}

DUNGEON = {
    "raid_id": 8,
    "title": "Todesminen",
    "raid_type": "special",
    "raid_size": 5,
    "signup_status": "open",
    "days": [_day("special", "2026-08-15T19:30:00+02:00", 3)],
    "dungeon": {"id": "the_deadmines", "name": "The Deadmines",
                "min_level": 17, "max_level": 26, "size": 5},
}


def test_parse_reads_dungeon_and_raid_has_none():

    schedule = parse_schedule({**RAID, "others": [DUNGEON]})

    assert schedule.dungeon is None
    assert schedule.others[0].dungeon.id == "the_deadmines"
    assert schedule.others[0].dungeon.min_level == 17


def test_only_dungeons_reach_the_addon():

    payload = build_payload(parse_schedule({**RAID, "others": [DUNGEON]}), NOW)

    assert payload["count"] == 1

    invite = payload["invites"][0]

    assert invite["dungeon"] == "the_deadmines"
    assert invite["active"] == 3
    assert invite["size"] == 5
    assert invite["me"] == "active"
    assert invite["open"] is True
    assert invite["at"] == int(datetime(2026, 8, 15, 17, 30, tzinfo=timezone.utc).timestamp())


def test_no_dungeon_is_an_explicit_empty_list():
    """Leer heißt "keine mehr" - die Nutzlast muss trotzdem kommen."""

    payload = build_payload(parse_schedule(RAID), NOW)

    assert payload == {"count": 0, "invites": []}


def test_past_invites_drop_out():

    past = {**DUNGEON, "status": "ok",
            "days": [_day("special", "2026-08-01T19:30:00+02:00")]}

    assert build_payload(parse_schedule(past), NOW)["count"] == 0


class _Inbox:
    def __init__(self):
        self.calls = []

    def publish(self, channel, messages):
        self.calls.append((channel, messages))
        return True


class _Logger:
    def success(self, text):
        pass


class _Manager:
    logger = _Logger()


def test_sync_publishes_only_on_change():

    inbox = _Inbox()
    sync = DungeonInviteSync(_Manager(), inbox)
    schedule = parse_schedule({**RAID, "others": [DUNGEON]})

    assert sync.process(schedule) is True
    assert sync.process(schedule) is False
    assert inbox.calls[0][0] == "dungeons"
    assert inbox.calls[0][1][0]["type"] == "dungeon_invites"
