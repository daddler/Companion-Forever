"""
Bestand aller Charaktere: Leser für den Spielstand und die Regeln
`unbekannt ≠ 0` für Bank und Gold.
"""

from core.inventory import load, merge, money_text, parse_inventory, read_file
from core.lua_reader import read_variable


SAVED = '''
WeintCodex_SavedDataOld = {
}
WeintCodex_SavedData = {
	["inventory"] = {
		["names"] = {
			[2589] = "Leinenstoff",
			[118] = "Schwacher Heiltrank",
			[777] = "Klammer {zu} \\"Zitat\\"",
		},
		["chars"] = {
			["Thrall|Weint"] = {
				["name"] = "Weint",
				["realm"] = "Thrall",
				["class"] = "MAGE",
				["bags"] = {
					[2589] = 12,
					[118] = 3,
				},
				["worn"] = {
				},
				["money"] = 1234567,
				["at"] = 100,
			},
			["Thrall|Twink"] = {
				["name"] = "Twink",
				["realm"] = "Thrall",
				["class"] = "WARRIOR",
				["bags"] = {
					[2589] = 5,
				},
				["bank"] = {
					[2589] = 20,
				},
				["at"] = 50,
			},
		},
	},
	["list"] = {
		"a", -- [1]
		true, -- [2]
		-1.5, -- [3]
	},
}
'''


def test_read_variable_skips_prefix_names_and_reads_values():

    saved = read_variable(SAVED, "WeintCodex_SavedData")

    assert saved["list"] == {1: "a", 2: True, 3: -1.5}

    assert saved["inventory"]["names"][777] == 'Klammer {zu} "Zitat"'


def test_umlauts_survive():

    saved = read_variable('X = {\n["n"] = "B\xc3\xa4r",\n}\n', "X")

    assert saved["n"] == "Bär"


def test_unknown_bank_and_gold_are_not_zero():

    inventory = parse_inventory(read_variable(SAVED, "WeintCodex_SavedData"))

    assert inventory.known

    total, unknown = inventory.gold()

    assert total == 1234567
    assert unknown == 1

    weint = next(c for c in inventory.characters if c.name == "Weint")

    assert weint.bank is None

    assert inventory.bank_unknown() == 1


def test_search_by_name_and_number():

    inventory = parse_inventory(read_variable(SAVED, "WeintCodex_SavedData"))

    [linen] = inventory.search("leinen")

    assert linen.total == 37

    assert [h.character.name for h in linen.holders] == ["Twink", "Weint"]

    assert linen.holders[0].where() == "Taschen 5 · Bank 20"

    assert [i.item_id for i in inventory.search("118")] == [118]

    assert inventory.search("gibtsnicht") == []


def test_no_inventory_is_unknown_not_empty():

    assert not parse_inventory({}).known

    assert not parse_inventory(None).known


def test_merge_prefers_newer_and_load_reads_accounts(tmp_path):

    for account, at in (("A", 100), ("B", 300)):

        folder = tmp_path / "WTF" / "Account" / account / "SavedVariables"

        folder.mkdir(parents=True)

        (folder / "WeintCodex.lua").write_text(
            SAVED.replace('["at"] = 100', f'["at"] = {at}'),
            encoding="utf-8",
        )

    inventory = load(tmp_path)

    assert len(inventory.characters) == 2

    weint = next(c for c in inventory.characters if c.name == "Weint")

    assert weint.at == 300

    assert merge([]).known is False


def test_broken_file_reports_error(tmp_path):

    path = tmp_path / "WeintCodex.lua"

    path.write_text("WeintCodex_SavedData = {\n[\"a\"] = ", encoding="utf-8")

    inventory = read_file(path)

    assert not inventory.known

    assert inventory.error


def test_money_text():

    assert money_text(1234567) == "123 g 45 s"

    assert money_text(123456789) == "12.345 g 67 s"

    assert money_text(305) == "3 s 5 k"
