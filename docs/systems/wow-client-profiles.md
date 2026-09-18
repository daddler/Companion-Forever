# Game versions: the table with one entry

*Which* World of Warcraft this app serves is a table entry
(`core/wow_clients.py`), not an assumption spread across the code. Since
5.0 that table holds exactly one row — Forever — and it is still a
table. This page explains why, what reads it, and **what has to change
when Forever ships.**

## Why a table with one entry

Because the mistake it prevents does not depend on its length.

Until 4.0 "WoW" silently meant Mists of Pandaria Classic, and the folder
name `_classic_` was written into six places: the folder check, the disk
search, the config key, three labels. A game version was not an object
in this app; it was a premise — and when a second one appeared, the
change was bigger than the change.

Forever has **not shipped yet** (4 November 2026). There will therefore
be at least one more moment where something here changes: when the
folder name is settled. That this is a line and not a rebuild is the
entire purpose of this file.

## The table

`core/wow_clients.py` holds one `WowClient` per game version:

| Field | Meaning |
|---|---|
| `id` | Key in `config.json` (`"forever"`) |
| `name` / `short_name` | Headings and dialogs / status lines |
| `folder_names` | Installation folder under the Battle.net root. **Empty means "not known yet"**; `_forever_` today is a guess |
| `max_level` | Level cap, or `None` while unknown |
| `released` | Offered during setup? |
| `hint` | One line shown under the picker |
| `markers` | What identifies an installation (default: `Interface/`, `Interface/AddOns/`, `WTF/`) |

`FOREIGN_FLAVOR_FOLDERS` lists every folder name Blizzard hands out to a
game version (`_retail_`, `_classic_`, `_classic_era_`, PTR/beta
variants). It is irrelevant for a client whose own folder name is known,
and it is the difference between "some installation" and "the right one"
for a client whose name is not.

## One unknown about Forever, and one that is settled

**The folder name is a guess.** Blizzard has named the sub-folders
under "World of Warcraft" `_retail_`, `_classic_`, `_classic_era_` since
forever; `_forever_` is the obvious continuation of that series and
nothing more. The beta was observed running in `_classic_beta_` — the
folder Blizzard uses for *every* Classic beta, which is why it stays in
`FOREIGN_FLAVOR_FOLDERS` rather than being claimed here. Handing a
leftover installation from one of those out as Forever is exactly the
silent mix-up that list exists to prevent.

The search therefore does **not** stand or fall with the guess. If it
holds, detection is one step quicker; if it does not, the markers find
the installation anyway:

- a *known* `folder_names` entry is looked for directly under the chosen
  root;
- if it does not match, only the installation markers decide
  (`Interface/AddOns`, `WTF`), and other game versions are excluded via
  `FOREIGN_FLAVOR_FOLDERS`.

**The level cap is settled: Forever stays at 60.** `max_level=None`
("unknown") is therefore history for this version — but the case stays
in the type, because it will come up again for every future version, and
`character_store.default_min_level()` already handles it correctly: it
answers `1`, so while a cap is unknown no character disappears from
"Meine Charaktere" because of an invented number. Same line as
`stars == 0` and `at == -1` — a gap in the data never becomes a
finding.

## Resolving a folder

`core/wow_folder.py`'s `check_client_folder()` returns a `FolderCheck`
(`path` plus a German `reason`, same shape as `CombatLogLocation`), in
this order:

1. The chosen folder itself carries the markers → it is the one.
2. A known `folder_names` entry directly below it — most users pick the
   `World of Warcraft` root, not the subfolder.
3. **Exactly one** subfolder carrying the markers and not named after
   another game version.

Step 3 is what carries Forever before its folder name is known. Several
candidates are **not guessed between**: a wrong guess would install the
addon into a copy of the game that is never launched, and nothing about
that failure would be visible — so the reason says "pick the subfolder
yourself" instead.

`addon/finder.py` (the automatic search at first start) follows the same
split: exact name match for a known client, markers-only for an unknown
one, foreign flavor folders skipped and never descended into. That
search is convenience; the manual pick is the reliable answer.

## One path per game version

`config.json` carries `wow_client` (the active id) and `wow_paths`
(`{id: path}`). Two versions, two paths — switching there and back
forgets nothing, which is the whole reason the switch is a toggle and
not a second folder button.

`classic_path` and `wow_paths["mop_classic"]` stay in the file as the
pre-5.0 spellings. They are **not read** — a migrating user's MoP folder
must never become the Forever path, because installing the addon into
the wrong game version is not undoable and nothing about it would be
visible. They are not deleted either: it is the same file an older
Companion reads if someone rolls back, and leaving them costs two lines
while removing them costs that user their folder.

`Config.get_wow_client_id()` **resolves** the stored id instead of
handing it out raw. Every migrating config still says `mop_classic`;
unresolved, `get_wow_path()` would key into `wow_paths["mop_classic"]`
and hand back exactly the folder above. One line, one place, and the
whole class of mistake is gone — which is why the resolution lives in
the accessor and not in each caller.

## What reads the client

| Reads | For |
|---|---|
| `core/wow_folder.py` | Which folder is valid |
| `addon/finder.py` | What to search for |
| `core/config.py` | Active id, per-version paths, level-cap migration |
| `core/companion_manager.py` | `detect_wow()`; a version change invalidates the sync markers exactly like a path change |
| `core/character_store.py` | Default minimum level |
| `gui/pages/settings_sections/wow_client.py` | The installation folder |
| `gui/dialogs/setup_wizard.py` | Step 1 — asks for the version **only** when more than one is released, so today it never asks |
| `gui/pages/connections.py`, `.../about.py` | Labels |

## When Forever ships: the checklist

**In this table** (`core/wow_clients.py`):

1. `folder_names=("_forever_",)` — confirm or correct it. Today it is a
   *guess* from Blizzard's naming convention (`_retail_`, `_classic_`,
   `_classic_era_`); the beta was observed running in `_classic_beta_`,
   which stays in `FOREIGN_FLAVOR_FOLDERS` because every Classic beta
   uses it. A wrong guess is harmless — detection falls back to the
   installation markers.
2. `released=True`. Setup step 1 starts offering the version by itself;
   no UI change needed.

That is the whole list for this file, and that was the point of the
table.

**Outside this table** — the client entry does *not* make the app
Forever-ready, and pretending otherwise would be the real trap. What is
played is a different question from where it is installed, and the
answer is not published yet: boss lists, per-spec abilities and the
class lesson catalog are deliberately **empty**. That has its own
document, including what fills them and in which order:
`forever-data.md`.

One thing outside both: the addon (`../WeintCodex`) needs a new
`## Interface:` in its `.toc` — the sibling repo's business, and a
bigger one than a number, because Forever runs on the modern client API.
