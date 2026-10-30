"""
Preisverläufe des Auktionshauses - gesammelt aus dem Spielstand des Addons.

WeintCodex liest beim Scan das günstigste Angebot je Stück
(`WeintCodex_SavedData.auction["Realm|Seite"]`, Aufbau:
`../Codex-Forever/ui/auctionprices.lua`): `items[id]` ist eine gepackte
Zahl (Preis, Menge, Tag, "von Spielern"), `hist[id]` der Verlauf der
letzten **7** Tage als `"Tag:Preis,…"`, seit Addon 1.8.1.0 `names[id]`.
Länger behält das Addon nichts - der Spielstand soll klein bleiben.

Diese App behält mehr: bei jedem Einlesen kommt dazu, was neu ist, in
`auction_history.json` im eigenen Datenordner (bis `KEEP_DAYS`). Daraus
die Frage, die im Spiel keiner beantworten kann: *ist das heute billig?*

Regeln, wie überall:

* **Nur eigene Scans.** Preise "von Spielern" (Gilde, fremder Kanal)
  stehen im Spiel im Tooltip, aber nicht im Verlauf - ein Preis, den
  jemand anderes gemeldet hat, ist keine Messung von dir.
* **Ein Tag, ein Preis**: das günstigste Angebot des Tages.
* **Zu wenig Verlauf ist kein Trend.** Unter `MIN_DAYS` Tagen vor dem
  letzten Preis gibt es keinen Schnitt und keine Prozentzahl (`None`),
  nie 0 %.
* **Ohne Namen eine Nummer.** Geraten wird kein Name.

Reiner Python-Teil, ohne Qt. Gelesen und geschrieben im Thread des
Laders, nie in `refresh()`. **Stand, nicht live**: das Spiel schreibt
den Spielstand beim Ausloggen.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from core.lua_reader import LuaReadError, read_variable


VARIABLE = "WeintCodex_SavedData"

FILE_NAME = "auction_history.json"

KEEP_DAYS = 365

WEEK = 7

MIN_DAYS = 2

#
# Wie im Addon (AP.Pack): Preis * 1e7 + Menge * 1e4 + Tag (+ 5000 = von
# Spielern). Tag 0 = 1.1.2026, Ortszeit des Spielers.
#

SHARED = 5000

BASE_DAY = _dt.date(2026, 1, 1)

SIDES = {"Alliance": "Allianz", "Horde": "Horde", "Neutral": "Neutral"}


def unpack(value) -> tuple[int, int, int, bool]:

    value = int(value)

    price = value // 10_000_000

    rest = value - price * 10_000_000

    qty = rest // 10_000

    day = rest - qty * 10_000

    if day >= SHARED:
        return price, qty, day - SHARED, True

    return price, qty, day, False


def day_date(day: int) -> _dt.date:

    return BASE_DAY + _dt.timedelta(days=int(day))


def money_text(copper: int) -> str:
    """"12 g 34 s 5 k" - kurz, ohne leere Stellen vorn."""

    copper = int(copper)

    gold, silver, cop = copper // 10000, (copper % 10000) // 100, copper % 100

    parts = []

    if gold:
        parts.append(f"{gold:,}".replace(",", ".") + " g")

    if gold or silver:
        parts.append(f"{silver} s")

    parts.append(f"{cop} k")

    return " ".join(parts)


# --------------------------------------------------
# Aus dem Spielstand
# --------------------------------------------------


def parse_saved(saved) -> dict:
    """
    `{markt: {"names": {id: name}, "days": {id: {tag: preis}}}}` aus einem
    Spielstand - nur eigene Preise.
    """

    out: dict = {}

    auction = saved.get("auction") if isinstance(saved, dict) else None

    if not isinstance(auction, dict):
        return out

    for market, store in auction.items():

        if not isinstance(market, str) or not isinstance(store, dict):
            continue

        names, days = {}, {}

        for item_id, name in (store.get("names") or {}).items():

            if isinstance(item_id, int) and isinstance(name, str) and name:
                names[item_id] = name

        def note(item_id, day, price):

            if price <= 0:
                return

            per_item = days.setdefault(item_id, {})

            old = per_item.get(day)

            per_item[day] = price if old is None else min(old, price)

        for item_id, text in (store.get("hist") or {}).items():

            if not isinstance(item_id, int) or not isinstance(text, str):
                continue

            for part in text.split(","):

                day, _, price = part.partition(":")

                if day.isdigit() and price.isdigit():
                    note(item_id, int(day), int(price))

        for item_id, packed in (store.get("items") or {}).items():

            if not isinstance(item_id, int) or not isinstance(packed, (int, float)):
                continue

            price, _qty, day, shared = unpack(packed)

            if not shared:
                note(item_id, day, price)

        out[market] = {"names": names, "days": days}

    return out


# --------------------------------------------------
# Das Archiv dieser App
# --------------------------------------------------


@dataclass
class ItemTrend:

    item_id: int

    name: str

    price: int

    day: int

    #
    # Schnitt der Tage davor (bis WEEK), `None` bei zu wenig Verlauf.
    #

    average: int | None = None

    change: float | None = None

    history: list = field(default_factory=list)

    @property
    def label(self) -> str:

        return self.name or f"Gegenstand {self.item_id}"


@dataclass
class Market:

    key: str

    names: dict = field(default_factory=dict)

    days: dict = field(default_factory=dict)

    @property
    def label(self) -> str:

        realm, _, side = self.key.partition("|")

        return f"{realm} · {SIDES.get(side, side)}"

    def trend(self, item_id: int) -> ItemTrend | None:

        per_item = self.days.get(item_id)

        if not per_item:
            return None

        history = sorted(per_item.items())

        day, price = history[-1]

        before = [p for d, p in history[:-1] if day - d <= WEEK]

        average = change = None

        if len(before) >= MIN_DAYS:

            average = round(sum(before) / len(before))

            if average > 0:
                change = (price - average) / average * 100

        return ItemTrend(item_id, self.names.get(item_id, ""), price, day, average, change, history)

    def trends(self) -> list[ItemTrend]:

        return [t for t in (self.trend(i) for i in self.days) if t is not None]

    def movers(self, limit: int = 15) -> list[ItemTrend]:
        """Was sich gegenüber der Woche am meisten bewegt hat."""

        moving = [t for t in self.trends() if t.change is not None]

        moving.sort(key=lambda t: abs(t.change), reverse=True)

        return moving[:limit]

    def search(self, query: str, limit: int = 60) -> list[ItemTrend]:

        query = query.strip().lower()

        if not query:
            return []

        hits = []

        for item_id in self.days:

            name = self.names.get(item_id, "")

            if query == str(item_id) or (name and query in name.lower()):
                hits.append(self.trend(item_id))

        hits.sort(key=lambda t: t.label.lower())

        return hits[:limit]


@dataclass
class AuctionHistory:

    known: bool = False

    markets: list = field(default_factory=list)

    error: str = ""

    newest_day: int | None = None

    def market(self, key: str) -> Market | None:

        for market in self.markets:
            if market.key == key:
                return market

        return None


def merge_into(archive: dict, fresh: dict, today: int | None = None) -> dict:
    """Frisches ins Archiv, Ältestes nach KEEP_DAYS heraus."""

    for key, data in fresh.items():

        target = archive.setdefault(key, {"names": {}, "days": {}})

        target["names"].update(data["names"])

        for item_id, per_item in data["days"].items():

            have = target["days"].setdefault(item_id, {})

            for day, price in per_item.items():

                old = have.get(day)

                have[day] = price if old is None else min(old, price)

    if today is None:
        today = max(
            (d for m in archive.values() for p in m["days"].values() for d in p),
            default=0,
        )

    for data in archive.values():

        for item_id in list(data["days"]):

            per_item = {d: p for d, p in data["days"][item_id].items() if today - d <= KEEP_DAYS}

            if per_item:
                data["days"][item_id] = per_item

            else:
                del data["days"][item_id]
                data["names"].pop(item_id, None)

    return archive


def archive_path() -> Path:

    from core.paths import Paths

    return Paths.base() / FILE_NAME


def read_archive(path: Path) -> dict:

    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))

    except (OSError, ValueError):
        return {}

    out = {}

    for key, data in (raw or {}).items():

        if not isinstance(data, dict):
            continue

        names = {int(i): n for i, n in (data.get("names") or {}).items() if str(i).isdigit()}

        days = {}

        for i, per_item in (data.get("days") or {}).items():

            if str(i).isdigit() and isinstance(per_item, dict):
                days[int(i)] = {int(d): int(p) for d, p in per_item.items() if str(d).isdigit()}

        out[key] = {"names": names, "days": days}

    return out


def write_archive(path: Path, archive: dict):

    path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        key: {
            "names": {str(i): n for i, n in m["names"].items()},
            "days": {str(i): {str(d): p for d, p in per.items()} for i, per in m["days"].items()},
        }
        for key, m in archive.items()
    }

    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".auction_", suffix=".json")

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, separators=(",", ":"))

        os.replace(tmp, path)

    except OSError:

        try:
            os.unlink(tmp)

        except OSError:
            pass

        raise


def build(archive: dict) -> AuctionHistory:

    markets = [
        Market(key, data["names"], data["days"])
        for key, data in sorted(archive.items())
        if data["days"]
    ]

    newest = max((d for m in markets for p in m.days.values() for d in p), default=None)

    return AuctionHistory(known=bool(markets), markets=markets, newest_day=newest)


def load(wow_path, addon_path=None, path: Path | None = None) -> AuctionHistory:
    """
    Spielstände lesen, ins Archiv mischen, Archiv schreiben.

    Liest und schreibt Dateien - deshalb im Thread des Laders, nie aus
    `refresh()`.
    """

    from core.backup import saved_variable_files

    path = path or archive_path()

    archive = read_archive(path)

    errors = []

    fresh_any = False

    for file in saved_variable_files(wow_path):

        try:
            text = Path(file).read_text(encoding="latin-1")

            saved = read_variable(text, VARIABLE)

        except (OSError, LuaReadError, RecursionError, IndexError) as exc:
            errors.append(f"{Path(file).name}: {exc}")
            continue

        fresh = parse_saved(saved)

        if fresh:
            fresh_any = True
            merge_into(archive, fresh)

    if fresh_any:

        try:
            write_archive(path, archive)

        except OSError as exc:
            errors.append(f"{FILE_NAME}: {exc}")

    result = build(archive)

    result.error = "; ".join(errors)

    return result
