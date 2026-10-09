# Bestand: inventory of all characters (since 5.1)

## Where the data comes from

WeintCodex ≥ 6.24.0.0 keeps, per character, bags, worn gear, the bank
(only while it was open) and since 6.26.0.0 gold, in
`WeintCodex_SavedData.inventory` (account-wide SavedVariables,
`WTF/Account/<acc>/SavedVariables/WeintCodex.lua`). Shape and rules on
the addon side: `../Codex-Forever/ui/inventory.lua`.

```
inventory = {
  names = { [itemID] = "Name", ... },          -- only items seen in a bag
  chars = { ["Realm|Name"] = {
      name, realm, class, faction,
      bags = { [itemID] = count }, worn = {...},
      bank = {...} | nil,  bankAt,               -- nil = never opened
      money = copper | nil, moneyAt, at } },
}
```

**This app only reads that file.** WoW writes it on logout;
`upsert_variable()` stays the one place this app writes SavedVariables.

## Reading it

- `core/lua_reader.py` — a reader for exactly what WoW writes (tables,
  strings with escapes, numbers, booleans, nil, `-- [n]` comments).
  Nothing is evaluated. Strings come back as UTF-8 (WoW writes bytes).
  `read_variable()` only matches an assignment at line start, so
  `WeintCodex_SavedDataOld` is not `WeintCodex_SavedData`.
- `core/inventory.py` (pure) — `parse_inventory()`, `merge()` over all
  accounts (same character twice → newer `at` wins), `search()` by name
  substring or exact item id. An item without a known name is findable
  by id only; no name is guessed.
- `gui/controllers/inventory_loader.py` — one loader per manager,
  shared by the Overview's gold tile and the Bestand page. Reads in a
  short-lived thread, only when mtime/size of a file changed, result via
  signal into the main thread.

## The three "unknown"s (`unknown ≠ 0`)

- No inventory at all (`Inventory.known is False`): file missing, addon
  too old, or "Bestand merken" off. The page shows an empty state that
  names which of these (no folder / unreadable / not yet reported).
- `bank is None`: that character's bank was never open. The footer
  counts them; the tooltip says it per row.
- `money is None`: not logged in since 6.26.0.0. Never summed as 0;
  counted next to the total.

It is the state of each character's **last logout**, and the page says
so. Mail and auctions are not part of it.
