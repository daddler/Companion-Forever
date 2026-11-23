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


def test_one_character_under_two_realm_spellings_is_shown_once(tmp_path, monkeypatch):

    # Rückmeldung 1.0.9: „Shooty“ zweimal, einmal ohne Realm.
    store = _store(tmp_path, monkeypatch)
    client = store.client_id()
    store.data["Shooty"] = {"name": "Shooty", "realm": "", "level": 46, "updated": 100, "wow_client": client}
    store.data["Shooty-CAMWOWEU4Realm3PvE"] = {
        "name": "Shooty", "realm": "CAMWOWEU4Realm3PvE", "level": 49, "updated": 200, "wow_client": client}
    store.data["Echo-Other"] = {"name": "Echo", "realm": "Other", "level": 60, "updated": 1, "wow_client": client}
    store.data["Echo-Realm"] = {"name": "Echo", "realm": "Realm", "level": 60, "updated": 2, "wow_client": client}
    store.manager.config.data["character_main"] = "Shooty"

    assert store.merge_duplicates() == 1

    shooty = [s for s in store.characters() if s["name"] == "Shooty"]
    assert len(shooty) == 1 and shooty[0]["level"] == 49
    assert "Shooty" not in store.data
    assert store.main_key() == "Shooty-CAMWOWEU4Realm3PvE"
    # Wirklich verschiedene Realms bleiben getrennt.
    assert "Echo-Other" in store.data and "Echo-Realm" in store.data


def test_newest_report_without_realm_keeps_the_known_realm(tmp_path, monkeypatch):

    store = _store(tmp_path, monkeypatch)
    client = store.client_id()
    store.data["Shooty-My Realm"] = {"name": "Shooty", "realm": "My Realm", "level": 46, "updated": 100, "wow_client": client}
    store.data["Shooty"] = {"name": "Shooty", "realm": "", "level": 49, "updated": 200, "wow_client": client}
    store.set_tracked(store.data["Shooty"], False)
    store.set_tracked(store.data["Shooty-My Realm"], True)

    store.merge_duplicates()

    kept = store.data["Shooty-My Realm"]
    assert kept["level"] == 49 and kept["realm"] == "My Realm"
    assert "Shooty" not in store.data
    # Nur einer der beiden war ausgeblendet: der Charakter bleibt sichtbar.
    assert store.is_tracked(kept)
