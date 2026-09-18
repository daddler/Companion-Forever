# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working
with code in this repository. It is a **router**, not a knowledge base:
detailed system documentation lives under `docs/` and is loaded on demand
via the task-routing table below.

## What this is

WeintCompanion 5 — **Forever Edition** — is the official desktop
companion app for the World of Warcraft addon **WeintCodex**, for
*World of Warcraft: Forever*. It's a PySide6 (Qt6) desktop application
that installs/updates the addon, manages backups, and bridges data
between the in-game addon and the **WeintCodex Bot** (Discord bot) via a
small HTTP backend.

It grew out of the Mists of Pandaria companion (`daddler/WeintCompanion`)
by removal, not by rewrite — which is why its plumbing is mature and its
game data is empty. The old app keeps its own repository and its own
release channel; a later release of it will offer users a one-click
switch over to this one.

UI text, comments, and log messages are in German; code identifiers are
in English.

## Role in the ecosystem

WeintCompanion is the **hub** of the Weint ecosystem and, deliberately,
**the authoritative host for every cross-repo data contract**:
`docs/*.md` at this repo's top level (not under a subdirectory) documents
every wire format shared with WeintCodex and/or WeintCodex Bot — both
sibling repos' own `CLAUDE.md`/`docs/` point back here rather than
restating these contracts. When a task touches a shared message type,
HTTP endpoint, or `WCIMPORT` format, read the matching file here *first*;
it is the single source of truth.

```
WeintCodex (in-game Lua)  ↕ SavedVariables file, no network  ↔  WeintCompanion (this repo)
                                                                        ↕ HTTP :8765
WeintCodex Bot (Discord bot backend)  ←────────────────────────────────┘
```

- **WeintCodex** (`../WeintCodex`) — judges gear/rotation correctness;
  this app never re-derives what it decides, only renders/relays.
- **WeintCodex Bot** (`../WeintCodex-Bot`) — Discord bot backend; this
  app is the only thing that talks to its HTTP API.

## Critical invariants

- **A page's `refresh()` may only draw, never fetch or block.** A network
  call in `refresh()` combined with `state_changed` redraws is an
  infinite loop (root-caused once, guarded by a structural AST test).
  Detail: `docs/architecture/navigation.md`.
- **A painted widget reads the accent/theme in `paintEvent`, never in
  `__init__`**, and never connects a `lambda` to a `ThemeManager` signal
  (creates either a stale colour or a permanent reference leak). Detail:
  `docs/architecture/theming.md`.
- **Never hand one Qt event handler another one's event** (e.g. a
  `QCloseEvent` into a `hideEvent` handler) — segfaults with no Python
  traceback. Shared teardown goes in a plain, event-free, idempotent
  method. Detail: `docs/architecture/qt-pitfalls.md`.
- **A raid/pull is the central object; Live, Analyse, Lernen and Quelle
  are four perspectives on it, never four places.** The context header
  lives outside the view stack so it survives a perspective change, and
  `core/raid_context.py` is a *projection* over `RaidDataService` — never
  a second store for mode, archive selection or replay. Detail:
  `docs/systems/raid-center.md`.
- **`stars == 0` means "no data", never "bad"; `at == -1` means "no
  timestamp known", never second 0.** These two conventions cross every
  layer (analyzer, Academy, addon bridge) and must never be normalized
  away. Detail: `docs/systems/weinttv-academy.md`.
- **The game version is a table entry, never a hard-coded folder name.**
  `core/wow_clients.py` holds exactly one entry (Forever) and stays a
  table anyway: `_forever_` in it is a *guess*, detection falls back to
  installation markers, and `max_level=None` would mean *unknown*, never
  *none*. `Config.get_wow_client_id()` resolves the stored id before
  anyone keys off it — a migrating user still has `mop_classic` in their
  config, and reading their MoP folder as the Forever path would install
  the addon into the wrong game. Detail:
  `docs/systems/wow-client-profiles.md`.
- **The game-data tables are empty on purpose, and that is a documented
  state, not a gap.** `analyzer/data/avoidable.py` (boss mechanics),
  `analyzer/data/class_abilities.py` (per-spec abilities),
  `analyzer/data/encounters.py` (boss lists) and the class lesson
  modules under `analyzer/academy/lessons/classes/` carry no content:
  Forever reworks every class and its boss lists are unpublished.
  Never backfill them from Mists of Pandaria — that would accuse players
  of mistakes on mechanics they never meet. Tests that need a populated
  table build their own via the `demo_abilities` / `demo_lessons` /
  `demo_rules` / `demo_encounters` fixtures in `tests/conftest.py`.
- **A single 401 must never unlink a Discord account.** Detail:
  `docs/companion-auth.md`.
- **`upsert_variable()` (writing into the addon's SavedVariables) is the
  one place this app can lose user data** — always re-check size/mtime
  immediately before `os.replace()`. Detail:
  `docs/development/paths-and-storage.md`.
- **Every shared contract doc in `docs/*.md` is authoritative** — don't
  restate a wire format in a system doc under `docs/systems/`/
  `docs/architecture/`; point to the contract file instead.
- **Every release needs its `CHANGELOG.md` entry, checked by
  `scripts/check_version.py`** — same three-places rule as the addon.
  Detail: `docs/systems/update-system.md`.

## Development workflow

```bash
pip install -r requirements.txt && python app.py
pip install -r requirements-dev.txt && python -m pytest tests/ -q
```

See `docs/development/testing-and-build.md` for what the test suite
covers (including the five PySide6/offscreen tests) and the
Linux/Windows/AppImage build commands.

## Task routing — read only what the task needs

### Shared cross-repo contracts (this repo's `docs/*.md`, top level)

| Contract | File |
|---|---|
| Zugriffsprofile (`access_profile`) | `docs/access-profile-bridge.md` |
| Ausrüstungsstand (`character_sheet`) | `docs/character-sheet-bridge.md` |
| Live-Brücke (`companion_live.lua`, überlebt `/reload`) | `docs/live-bridge.md` |
| Raid-Termin, Countdown, Zusagen | `docs/raid-schedule-bridge.md` |
| WarcraftLogs Live/Archiv/Timeline | `docs/warcraftlogs-bridge.md` |
| WCIMPORT-Protokoll (Bot-Slash-Commands → Addon) | `docs/wcimport-protocol.md` |
| Charakterzuordnung, raid-roster, WeintAdmin-Backup | `docs/character-links-and-admin-bridge.md` |
| Academy/Rotationshelfer lokale Nachrichten | `docs/academy-and-practice-bridge.md` |
| Companion-Token/Auth, 401-Regel | `docs/companion-auth.md` |

### This repo's own architecture and pages

| Task touches… | Read |
|---|---|
| Theme/accent, signals, animations, lambda leaks | `docs/architecture/theming.md` |
| Page registry, `PageId`, `RaidView`/`RaidLink`, page lifecycle | `docs/architecture/navigation.md` |
| Qt segfaults, startup ordering, platform paths | `docs/architecture/qt-pitfalls.md` |
| Raid Center (Informationsarchitektur, vier Ansichten, RaidContext, Tiefenverweise) | `docs/systems/raid-center.md` |
| WeintTV/Academy (live), ratings, lesson catalog, "wer bin ich", Datenquelle/Quellenzeile/Wegweiser | `docs/systems/weinttv-academy.md` |
| Archiv-Modus, Wiedergabe/Replay | `docs/systems/archive-and-replay.md` |
| Addon-/Companion-Updates, Storage-Warnung, Changelog-Anzeige | `docs/systems/update-system.md` |
| Meine Charaktere, Vorbereitung, Charakterzuordnung-Seite | `docs/systems/character-pages.md` |
| Onboarding-Tour, "Was ist neu"-Popup | `docs/systems/whats-new-and-onboarding.md` |
| Spielversion, Client-Erkennung, Installationspfade | `docs/systems/wow-client-profiles.md` |
| Übersicht: Aufgabenkarte, Brücken-Kachel | `docs/systems/overview-page.md` |
| Spieldaten (leer): Bosse, Fähigkeiten, Lektionen | `docs/systems/forever-data.md` |
| Pfade, atomare Writes, Backups, Config/Auth-Speicherung | `docs/development/paths-and-storage.md` |
| Tests, Build, AppImage/Windows-Installer | `docs/development/testing-and-build.md` |
| "warum war das mal kaputt" | `docs/history/install-and-auth-incidents.md` |

Cross-repo tasks (touches Codex and/or Bot too): start with the matching
contract doc above, then follow its pointers into
`../WeintCodex/docs/` and/or `../WeintCodex-Bot/docs/` for each repo's
own implementation.
