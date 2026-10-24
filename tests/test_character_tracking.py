"""Main und Verfolgen (core/character_store.py, 5.4.0)."""

from core.character_store import CharacterStore


class _Config:
    def __init__(self):
        self.data = {"wow_client": "forever"}
        self.saved = 0

    def save(self):
        self.saved += 1

    def get_wow_client_id(self):
        return "forever"


class _Manager:
    def __init__(self):
        self.config = _Config()


def _store(tmp_path, monkeypatch):

    from core import character_store as cs_mod

    monkeypatch.setattr(cs_mod.Paths, "config", staticmethod(lambda: tmp_path))
    store = CharacterStore(_Manager())
    for name, level in (("Main", 60), ("Bank", 60), ("Alt", 60)):
        store.data[name + "-Realm"] = {
            "name": name, "realm": "Realm", "level": level,
            "updated": level, "wow_client": store.client_id(),
        }
    return store


def test_untracked_characters_leave_the_list_but_stay_stored(tmp_path, monkeypatch):

    store = _store(tmp_path, monkeypatch)
    bank = store.data["Bank-Realm"]

    store.set_tracked(bank, False)

    assert bank not in store.characters()
    assert store.untracked() == [bank]
    assert "Bank-Realm" in store.data
    assert store.manager.config.saved

    store.set_tracked(bank, True)
    assert bank in store.characters()


def test_the_main_comes_first_and_is_tracked(tmp_path, monkeypatch):

    store = _store(tmp_path, monkeypatch)
    alt = store.data["Alt-Realm"]

    store.set_tracked(alt, False)
    store.set_main(alt)

    assert store.characters()[0] is alt
    assert store.is_main(alt)

    store.set_tracked(alt, False)
    assert not store.is_main(alt)


def test_untracked_characters_are_not_reported_to_the_bot(tmp_path, monkeypatch):

    store = _store(tmp_path, monkeypatch)
    store.set_tracked(store.data["Bank-Realm"], False)

    assert store.filter_roster_payload(
        "Main|WARRIOR|Realm,Bank|MAGE|Realm,Bank|MAGE"
    ) == "Main|WARRIOR|Realm"
