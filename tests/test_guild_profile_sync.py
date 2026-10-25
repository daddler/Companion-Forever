"""
Berufe & Twinks an den Bot: was in der Meldung steht und wann sie geht.
"""

from types import SimpleNamespace

from core import guild_profile_sync
from core.guild_profile_sync import GuildProfileSync, build_payload
from core.professions import (
    CharacterProfession,
    CharacterProfessions,
    ProfessionInfo,
    Professions,
    Recipe,
)


CATALOG = {
    "tailoring": ProfessionInfo(
        "tailoring", "Schneiderei",
        recipes={3914: Recipe(3914, "Leinenstoffbeutel"), 18455: Recipe(18455, "Runenstoffbeutel")},
    ),
}

PROFS = Professions(
    known=True,
    catalog=CATALOG,
    characters=[
        CharacterProfessions(
            label="Weintmage-Everlook",
            professions=[
                CharacterProfession("tailoring", "Schneiderei", 215, 225, True, [18455, 3914, 99999]),
                CharacterProfession("enchanting", "Verzauberkunst", None, None, False, []),
            ],
        ),
        CharacterProfessions(label="Versteckt-Everlook", professions=[
            CharacterProfession("mining", "Bergbau", 100, 150, False, []),
        ]),
    ],
)

SHEETS = [
    {"name": "Weintmage", "realm": "Everlook", "class": "MAGE", "level": 34},
    {"name": "Neu", "realm": "Everlook", "class": "ROGUE", "level": 0},
]


def test_payload_names_recipes_and_keeps_unknown():

    payload = build_payload(SHEETS, PROFS, "forever")

    assert payload["wow_client"] == "forever"

    mage, new = payload["characters"]

    tailoring, enchanting = mage["professions"]

    assert tailoring["recipes"] == ["#99999", "Leinenstoffbeutel", "Runenstoffbeutel"]
    assert tailoring["rank"] == 215 and tailoring["max"] == 225
    assert enchanting["rank"] is None
    assert enchanting["scanned"] is False and "recipes" not in enchanting

    # Stufe 0 heißt "nicht bekannt", nicht Stufe 0.
    assert new["level"] is None and new["professions"] == []


def test_untracked_characters_never_leave():

    payload = build_payload(SHEETS, PROFS)

    assert [c["name"] for c in payload["characters"]] == ["Weintmage", "Neu"]


class _Store:

    def __init__(self, sheets):
        self.sheets = sheets

    def characters(self):
        return list(self.sheets)

    @staticmethod
    def key_of(sheet):
        return sheet["name"]


class _Logger:
    def __init__(self):
        self.lines = []

    def success(self, text):
        self.lines.append(text)

    info = success


def _manager(tmp_path):
    return SimpleNamespace(
        config=SimpleNamespace(data={}, get_wow_client_id=lambda: "forever"),
        state=SimpleNamespace(wow_path=tmp_path, addon_path=None),
        characters=_Store(SHEETS),
        logger=_Logger(),
    )


def test_sends_once_and_again_only_after_change(tmp_path, monkeypatch):

    sent = []

    class _Response:
        status_code = 200

    def fake_post(url, json, headers, timeout):
        sent.append(json)
        return _Response()

    monkeypatch.setattr(guild_profile_sync.httpx, "post", fake_post)
    monkeypatch.setattr(guild_profile_sync, "files_stamp", lambda path: (("a", 1, 1),))
    monkeypatch.setattr(guild_profile_sync, "CHECK_SECONDS", 0)
    monkeypatch.setattr("core.professions.load", lambda wow, addon: PROFS)

    sync = GuildProfileSync(_manager(tmp_path))
    monkeypatch.setattr(sync.account_store, "load", lambda: {"companion_token": "t"})

    assert sync.process() is True
    assert sync.process() is False
    assert len(sent) == 1

    # Twink ausgeblendet: keine Datei geändert, trotzdem neue Meldung.
    sync.manager.characters = _Store(SHEETS[:1])
    assert sync.process() is True
    assert [c["name"] for c in sent[-1]["characters"]] == ["Weintmage"]


def test_switched_off_sends_nothing(tmp_path, monkeypatch):

    manager = _manager(tmp_path)
    manager.config.data["profile_sync_enabled"] = False

    def boom(*a, **k):
        raise AssertionError("gesendet trotz Schalter aus")

    monkeypatch.setattr(guild_profile_sync.httpx, "post", boom)

    assert GuildProfileSync(manager).process() is False
