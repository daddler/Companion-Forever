"""1.0.5: Fehlerberichte - vorgemerkte Fehler gehen genau einmal an den Bot."""

from types import SimpleNamespace

from core import addon_errors, bug_report_sync
from core.addon_errors import parse_errors


class _Log:
    def __getattr__(self, name):
        return lambda *a, **k: None


class _Config:
    def __init__(self):
        self.data = {}

    def save(self):
        pass


def _manager(tmp_path):
    return SimpleNamespace(config=_Config(), logger=_Log(), state=SimpleNamespace(wow_path=tmp_path))


def test_parse_report_fields():
    saved = {"errors": {1: {"msg": "boom", "report": "pending", "reportAt": 123,
                            "client": "1.60.1 (1)", "class": "PRIEST", "level": 12, "zone": "Elwynn"}}}
    e = parse_errors(saved, "Konto").errors[0]
    assert e.report == "pending" and e.report_at == 123 and e.wow_class == "PRIEST" and e.level == "12"
    p = bug_report_sync.payload(e)
    assert p["message"] == "boom" and p["class"] == "PRIEST" and p["zone"] == "Elwynn"


def test_process_sends_once(tmp_path, monkeypatch):
    m = _manager(tmp_path)
    sync = bug_report_sync.BugReportSync(m)
    err = parse_errors({"errors": {1: {"msg": "boom", "report": "pending", "reportAt": 5}}}, "K").errors[0]
    calls = []
    monkeypatch.setattr(addon_errors, "load", lambda path: SimpleNamespace(errors=[err]))
    monkeypatch.setattr("core.guild_profile_sync.files_stamp", lambda p: (len(calls),))
    monkeypatch.setattr(sync.account_store, "load", lambda: {"companion_token": "t"})

    def post(url, json, headers, timeout):
        calls.append(json)
        return SimpleNamespace(status_code=200)

    monkeypatch.setattr(bug_report_sync.httpx, "post", post)
    assert sync.process() == 1
    sync._last_check = None
    assert sync.process() == 0
    assert len(calls) == 1 and sync.is_sent(err)


def test_failure_is_retried(tmp_path, monkeypatch):
    m = _manager(tmp_path)
    sync = bug_report_sync.BugReportSync(m)
    err = parse_errors({"errors": {1: {"msg": "boom", "report": "pending", "reportAt": 5}}}, "K").errors[0]
    monkeypatch.setattr(sync.account_store, "load", lambda: {"companion_token": "t"})
    monkeypatch.setattr(bug_report_sync.httpx, "post", lambda *a, **k: SimpleNamespace(status_code=502))
    ok, text = sync.send(err)
    assert not ok and not sync.is_sent(err) and "nicht angenommen" in text
