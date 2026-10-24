"""Berufe und Addon-Fehler aus dem Spielstand (neu in 1.0.0), ohne Qt."""

from core.addon_errors import parse_errors, report
from core.changelog_reader import read_changelog_sections
from core.professions import parse_catalog, parse_professions
from core.version import SWITCH_LABEL, is_forever_switch, update_label


CATALOG = '''
P.PROFS = {
    { key = "alchemy", spell = 2259, line = 171, cat = 1, name = "Alchemie" },
    { key = "cooking", spell = 2550, line = 185, cat = 3, name = "Kochkunst" },
}
P.RAW = {
    ["alchemy"] = [[
2332 2456 40 70 90 110 s t - -|785:2,2447:1,3371:1|Minor Rejuvenation Potion
7183 5997 1 55 75 95 c t - -|765:1|Elixir of Minor Defense
]],
}
'''


def test_catalog_reads_names_and_recipes():

    catalog = parse_catalog(CATALOG)

    assert catalog["alchemy"].name == "Alchemie"
    assert catalog["alchemy"].recipes[2332].name == "Minor Rejuvenation Potion"
    assert catalog["alchemy"].recipes[2332].learn == 40
    assert catalog["cooking"].recipes == {}


def test_unknown_rank_stays_unknown_and_unscanned_is_not_zero():

    saved = {"professions": {
        "Anna-Realm": {"known": {2332: True, 999: True}, "scanned": {"alchemy": 1}},
        "Bert-Realm": {"skills": {"cooking": {"rank": 75, "max": 150}}, "skillsAt": 5},
    }}

    data = parse_professions(saved, parse_catalog(CATALOG))

    anna, bert = data.characters

    alchemy = anna.professions[0]
    assert alchemy.rank is None
    assert alchemy.scanned is True
    assert alchemy.known == [2332]

    cooking = bert.professions[0]
    assert (cooking.rank, cooking.max, cooking.scanned) == (75, 150, False)

    assert data.who_can("rejuv") == [("Minor Rejuvenation Potion", "Alchemie", ["Anna-Realm"])]


def test_no_professions_table_is_not_known():

    assert parse_professions({}).known is False


def test_errors_parse_and_report():

    saved = {"errors": {1: {"kind": "blocked", "msg": "a\nb", "stack": "s", "count": 3,
                            "first": "1", "last": "2", "version": "1.0.0.0"}}}

    result = parse_errors(saved, "KONTO")

    assert result.known and len(result.errors) == 1
    e = result.errors[0]
    assert e.kind_label == "Vom Spiel blockiert" and e.headline == "a" and e.count == 3

    text = report(result.errors)
    assert "3x" in text and "Fassung 1.0.0.0" in text and "s" in text


def test_forever_switch_label_only_on_downward_version():

    assert is_forever_switch("6.146.0.0", "1.0.0.0")
    assert is_forever_switch("5.5.0", "1.0.0")
    assert not is_forever_switch("1.0.0", "1.0.1")
    assert not is_forever_switch("-", "1.0.0")
    assert update_label("5.5.0", "1.0.0", "x") == SWITCH_LABEL
    assert update_label("1.0.0", "1.1.0", "x") == "x"


def test_changelog_after_reset_shows_new_section():

    sections = read_changelog_sections("1.0.0", since_version="5.5.0")

    assert [v for v, _ in sections] == ["1.0.0"]


def test_beta_characters_are_wiped_once_for_upgraders(tmp_path, monkeypatch):

    import json
    from types import SimpleNamespace

    from core import character_store

    monkeypatch.setattr(character_store.Paths, "config", staticmethod(lambda: tmp_path))

    (tmp_path / "characters.json").write_text(json.dumps({"A-R": {"name": "A", "realm": "R"}}))

    data = {"onboarding_seen_version": "5.5.0"}

    logs = []

    manager = SimpleNamespace(
        config=SimpleNamespace(data=data, save=lambda: None),
        logger=SimpleNamespace(info=logs.append, warning=logs.append),
        state=SimpleNamespace(forever_folder_missing=False),
    )

    store = character_store.CharacterStore(manager)

    assert store.data == {}
    assert data[store.WIPE_KEY] is True
    assert (tmp_path / "characters.beta.json").exists()


def test_sheets_are_ignored_while_forever_folder_is_missing():

    from types import SimpleNamespace

    from core.character_store import CharacterStore

    store = CharacterStore.__new__(CharacterStore)
    store.manager = SimpleNamespace(state=SimpleNamespace(forever_folder_missing=True))

    assert store.apply("irrelevant") is None
