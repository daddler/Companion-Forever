"""
Aufträge in der Companion: lesen, ansagen, ans Addon geben, Status senden.
"""

from types import SimpleNamespace

from core import craft_orders
from core.craft_orders import CraftOrderSync, addon_payload, parse_orders


def _row(id, role="crafter", status="open", **kw):
    row = {"id": id, "role": role, "recipe": "Runenstoffbeutel", "character": "Weintmage",
           "profession": "Schneiderei", "quantity": 4, "note": "", "mats": True,
           "status": status, "requester_name": "Fabi", "created_at": 1}
    row.update(kw)
    return row


def _answer(*rows):
    return {"status": "ok", "orders": list(rows)}


def test_parse_skips_rubbish():

    orders = parse_orders(_answer(_row(1), {"id": "x"}, "kaputt"))

    assert [o.id for o in orders] == [1]
    assert orders[0].moves() == ("accepted", "done", "declined")
    assert parse_orders({"status": "idle"}) == ()


def test_requester_may_only_cancel():

    (order,) = parse_orders(_answer(_row(1, role="requester")))

    assert order.moves() == ("cancelled",)


def test_addon_gets_open_ones_and_never_an_empty_table():

    orders = parse_orders(_answer(_row(1), _row(2, status="done"), _row(3, note="per Post")))

    payload = addon_payload(orders)

    assert payload["count"] == 2
    assert [o["id"] for o in payload["orders"]] == [1, 3]
    assert payload["orders"][1]["note"] == "per Post"
    assert "note" not in payload["orders"][0]

    assert addon_payload(()) == {"count": 0, "orders": []}


class _Inbox:
    def __init__(self):
        self.calls = []

    def publish(self, channel, messages):
        self.calls.append((channel, messages))
        return True


class _Logger:
    def __init__(self):
        self.lines = []

    def success(self, text):
        self.lines.append(text)

    info = warning = success


def _sync():
    manager = SimpleNamespace(logger=_Logger())
    return CraftOrderSync(manager, _Inbox())


def test_first_fetch_announces_nothing_later_ones_do():

    sync = _sync()

    assert sync._take(parse_orders(_answer(_row(1)))) is True
    assert sync.take_new() == []                       # Start: nichts "neu"

    sync._take(parse_orders(_answer(_row(1), _row(2), _row(3, role="requester"))))
    assert [o.id for o in sync.take_new()] == [2]       # nur eingehende
    assert sync.take_new() == []                        # nur einmal

    assert sync.inbox.calls[-1][0] == "orders"
    assert sync.inbox.calls[-1][1][0]["type"] == "craft_orders"


def test_addon_written_only_on_change():

    sync = _sync()
    orders = parse_orders(_answer(_row(1)))

    sync._take(orders)
    sync._take(orders)

    assert len(sync.inbox.calls) == 1


class _Response:
    def __init__(self, code, body=None):
        self.status_code = code
        self._body = body or {}

    def json(self):
        return self._body


def test_send_status_results(monkeypatch):

    sync = _sync()
    monkeypatch.setattr(sync.account_store, "load", lambda: {"companion_token": "t"})

    codes = iter([200, 409, 502])
    sent = []

    def post(url, json, headers, timeout):
        sent.append((url, json))
        return _Response(next(codes), {"detail": "schon erledigt"})

    monkeypatch.setattr(craft_orders.httpx, "post", post)

    assert sync.send_status(5, "accepted", "codex") == "ok"
    assert sent[0] == (f"{craft_orders.BOT_BASE_URL}/companion/orders/5/status",
                       {"status": "accepted", "via": "codex"})
    assert sync.send_status(5, "accepted", "codex") == "rejected"
    assert sync.send_status(5, "accepted", "codex") == "retry"


class _Reader:
    def __init__(self, messages):
        self.messages = list(messages)
        self.removed = []
        self.wow_path = None

    def exists(self):
        return True

    def get_messages(self):
        return list(self.messages)

    def remove_message(self, message_id):
        self.removed.append(message_id)


def _sync_manager(messages, result):

    from core.sync_manager import SyncManager

    calls = []

    class Orders:
        def send_status(self, order_id, status, via):
            calls.append((order_id, status, via))
            return result

    manager = SimpleNamespace(
        state=SimpleNamespace(wow_path=None),
        logger=_Logger(),
        config=SimpleNamespace(data={}),
        craft_order_sync=Orders(),
    )

    sync = SyncManager.__new__(SyncManager)
    sync.manager = manager
    sync.reader = _Reader(messages)
    return sync, calls


def test_click_in_codex_reaches_the_bot():

    sync, calls = _sync_manager([{"id": 7, "type": "craft_order_status", "payload": "12|done"}], "ok")
    sync.process()

    assert calls == [(12, "done", "codex")]
    assert sync.reader.removed == [7]


def test_bot_unreachable_keeps_the_click():

    sync, _ = _sync_manager([{"id": 7, "type": "craft_order_status", "payload": "12|done"}], "retry")
    sync.process()

    assert sync.reader.removed == []


def test_rejected_click_is_dropped():

    sync, _ = _sync_manager([{"id": 7, "type": "craft_order_status", "payload": "12|done"}], "rejected")
    sync.process()

    assert sync.reader.removed == [7]
