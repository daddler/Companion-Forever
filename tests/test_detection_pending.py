"""
1.0.4: Solange die erste Suche nach WeintCodex nicht fertig ist, wird
nichts installiert - gemeldet: nach dem Rechnerstart bot die App
"installieren" an, obwohl die Suche noch lief (und ohne erkanntes Addon
entsteht vor dem Ueberschreiben kein Backup der SavedVariables).
"""

from types import SimpleNamespace

from core.app_state import AppState
from core.installer_workflow import InstallerWorkflow


class _Log:
    def __init__(self):
        self.lines = []

    def __getattr__(self, name):
        return lambda msg, *a, **k: self.lines.append((name, msg))


def test_state_starts_unchecked():
    assert AppState().addon_checked is False


def test_workflow_refuses_while_searching():
    state = AppState()
    state.github_download_url = "https://example.invalid/x.zip"
    manager = SimpleNamespace(state=state, logger=_Log())
    result = InstallerWorkflow(manager).run()
    assert result.success is False
    assert "Suche" in result.message
