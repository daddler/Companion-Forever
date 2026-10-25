"""
Aufträge in der Gilde - abholen, melden, weitergeben, Status setzen.

Ein Auftrag entsteht im Discord (Rezeptsuche im Berufe-Channel). Der
Bot hält ihn; diese Datei holt alle Aufträge des Spielers ab – die, die
er herstellen soll (`role == "crafter"`), und die, die er selbst
aufgegeben hat (`"requester"`). Vertrag: `docs/craft-orders-bridge.md`.

Drei Wege, auf denen ein Hersteller den Status setzt, alle drei landen
beim Bot (`POST /companion/orders/<id>/status`):

* im Discord (DM mit Knöpfen) – geht direkt an den Bot, nicht hierher;
* hier in der Companion (Seite *Berufe*, Abschnitt *Aufträge*);
* in WeintCodex – das Addon reiht `craft_order_status` in seine
  Warteschlange, `core/sync_manager.py` reicht sie über `send_status()`
  weiter (erst nach Ausloggen oder `/reload`: das Spiel schreibt die
  Datei nicht früher).

Ins Spiel gehen die Aufträge über die Inbox (Kanal `orders`, Typ
`craft_orders`) – **immer der volle Stand**, eine leere Liste heißt
„keine“. Ankommen tun sie dort beim nächsten Einloggen oder `/reload`;
schneller lässt das Spiel ein Addon keine Datei lesen. Deshalb sagt
die Companion einen neuen Auftrag sofort selbst an (`take_new()`).
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass

import httpx

from core.backend_config import BOT_BASE_URL
from core.discord_account import DiscordAccountStore


CHANNEL = "orders"

MESSAGE_TYPE = "craft_orders"

STATUS_MESSAGE = "craft_order_status"

REFRESH_SECONDS = 60

TIMEOUT = 20

STATUS_LABELS = {
    "open": "offen",
    "accepted": "angenommen",
    "declined": "abgelehnt",
    "done": "erledigt",
    "cancelled": "storniert",
}

FINAL = {"declined", "done", "cancelled"}

# Was wer von wo aus darf – dieselben Regeln wie im Bot
# (services/craft_orders.py); hier nur, um keine Knöpfe anzubieten,
# die der Bot ablehnen würde. Entscheiden tut der Bot.
CRAFTER_MOVES = {
    "open": ("accepted", "done", "declined"),
    "accepted": ("done", "declined"),
}

REQUESTER_MOVES = {
    "open": ("cancelled",),
    "accepted": ("cancelled",),
}


@dataclass(frozen=True)
class CraftOrder:

    id: int
    role: str
    recipe: str
    character: str
    profession: str
    quantity: int
    note: str
    mats: bool
    status: str
    requester_name: str
    created_at: int = 0

    @property
    def status_label(self) -> str:
        return STATUS_LABELS.get(self.status, self.status)

    @property
    def is_open(self) -> bool:
        return self.status not in FINAL

    def moves(self) -> tuple:
        table = CRAFTER_MOVES if self.role == "crafter" else REQUESTER_MOVES
        return table.get(self.status, ())

    def title(self) -> str:
        return f"{self.quantity}× {self.recipe}"


def parse_orders(data) -> tuple[CraftOrder, ...]:
    """Antwort von GET /companion/orders. Unbrauchbares fällt weg."""

    if not isinstance(data, dict) or data.get("status") != "ok":
        return ()

    out = []

    for row in data.get("orders") or []:

        if not isinstance(row, dict):
            continue

        try:
            out.append(CraftOrder(
                id=int(row["id"]),
                role="crafter" if row.get("role") == "crafter" else "requester",
                recipe=str(row.get("recipe") or ""),
                character=str(row.get("character") or ""),
                profession=str(row.get("profession") or ""),
                quantity=int(row.get("quantity") or 1),
                note=str(row.get("note") or ""),
                mats=bool(row.get("mats")),
                status=str(row.get("status") or "open"),
                requester_name=str(row.get("requester_name") or ""),
                created_at=int(row.get("created_at") or 0),
            ))
        except (KeyError, TypeError, ValueError):
            continue

    return tuple(out)


def addon_payload(orders) -> dict:
    """
    Was WeintCodex bekommt: die offenen und angenommenen Aufträge, die
    der Spieler herstellen soll, plus seine eigenen offenen Bestellungen.
    Nie leer als Tabelle (`count` steht immer da) - die Inbox lässt eine
    leere Nutzlast weg, und dann bliebe im Spiel ein alter Stand stehen.
    """

    rows = []

    for order in orders:

        if not order.is_open:
            continue

        row = {
            "id": order.id,
            "role": order.role,
            "recipe": order.recipe,
            "character": order.character,
            "quantity": order.quantity,
            "mats": order.mats,
            "status": order.status,
            "from": order.requester_name,
        }

        if order.note:
            row["note"] = order.note

        rows.append(row)

    return {"count": len(rows), "orders": rows}


class CraftOrderSync:

    def __init__(self, manager, inbox):

        self.manager = manager

        self.inbox = inbox

        self.account_store = DiscordAccountStore()

        self.orders: tuple[CraftOrder, ...] = ()

        self.known = False

        self._last_fetch = None

        self._delivered = None

        self._seen: set[int] | None = None

        self._new: list[CraftOrder] = []

        self._lock = threading.Lock()

    # --------------------------------------------------

    def _token(self) -> str | None:

        account = self.account_store.load()

        return account.get("companion_token") if account else None

    def invalidate(self):

        self._last_fetch = None

    def process(self) -> bool:
        """Abrufen (höchstens jede Minute). True, wenn sich etwas geändert hat."""

        token = self._token()

        if not token:
            return False

        now = time.monotonic()

        if self._last_fetch is not None and now - self._last_fetch < REFRESH_SECONDS:
            return False

        self._last_fetch = now

        try:
            response = httpx.get(
                f"{BOT_BASE_URL}/companion/orders",
                headers={"Authorization": f"Bearer {token}"},
                timeout=TIMEOUT,
            )
        except Exception as exc:
            self.manager.logger.info(f"Aufträge nicht abrufbar: {exc}")
            return False

        if response.status_code == 401:
            self.account_store.note_auth_rejected()
            return False

        if response.status_code != 200:
            # 404: ältere Bot-Fassung ohne Aufträge - still.
            return False

        try:
            orders = parse_orders(response.json())
        except ValueError:
            return False

        return self._take(orders)

    def _take(self, orders) -> bool:

        with self._lock:

            changed = orders != self.orders or not self.known

            incoming = {o.id for o in orders if o.role == "crafter" and o.status == "open"}

            #
            # Beim ersten Abruf nach dem Start ist nichts "neu": sonst
            # meldete jeder Start alle offenen Aufträge noch einmal.
            #

            if self._seen is None:
                self._seen = set(incoming)
            else:
                for order in orders:
                    if order.id in incoming and order.id not in self._seen:
                        self._new.append(order)
                        self._seen.add(order.id)

            self.orders = orders
            self.known = True

        self._deliver()

        return changed

    def _deliver(self):

        payload = addon_payload(self.orders)

        if payload == self._delivered:
            return

        if self.inbox.publish(CHANNEL, [{"type": MESSAGE_TYPE, "payload": payload}]):
            self._delivered = payload

    def take_new(self) -> list[CraftOrder]:
        """Die seit dem letzten Aufruf neu eingegangenen Aufträge (für die Ansage)."""

        with self._lock:
            new, self._new = self._new, []

        return new

    # --------------------------------------------------

    def send_status(self, order_id: int, status: str, via: str) -> str:
        """
        Setzt einen Status beim Bot. Blockiert - nie aus `refresh()`.

        Ergebnis: "ok", "rejected" (409/400: geht nicht mehr - verwerfen)
        oder "retry" (Netz, 5xx: später noch einmal).
        """

        token = self._token()

        if not token:
            return "retry"

        try:
            response = httpx.post(
                f"{BOT_BASE_URL}/companion/orders/{int(order_id)}/status",
                json={"status": status, "via": via},
                headers={"Authorization": f"Bearer {token}"},
                timeout=TIMEOUT,
            )
        except Exception as exc:
            self.manager.logger.info(f"Auftragsstatus nicht gesendet: {exc}")
            return "retry"

        if response.status_code == 200:

            self.manager.logger.success(
                f"Auftrag #{order_id}: {STATUS_LABELS.get(status, status)}."
            )

            self.invalidate()

            return "ok"

        if response.status_code in (400, 404, 409):

            detail = ""

            try:
                detail = response.json().get("detail", "")
            except ValueError:
                pass

            self.manager.logger.warning(
                f"Auftrag #{order_id} nicht geändert: {detail or response.status_code}"
            )

            return "rejected"

        if response.status_code == 401:
            self.account_store.note_auth_rejected()

        return "retry"

    def set_status_async(self, order_id: int, status: str, done=None):
        """Für die Oberfläche: im eigenen Thread senden, dann neu abrufen."""

        def worker():

            result = self.send_status(order_id, status, "companion")

            if result == "ok":
                self.process()

            if done is not None:
                done(result)

        threading.Thread(target=worker, daemon=True, name="CraftOrderStatus").start()
