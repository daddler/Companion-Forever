"""
Nur eine Companion (1.0.8, core/single_instance.py).

Gemeldet aus einem Stream: Companion geschlossen (lief im Tray weiter),
erneut gestartet, am Ende vier parallel. Ein zweiter Start meldet sich
jetzt bei der laufenden und endet; die holt ihr Fenster. Beim Beenden
gibt die erste den Kanal frei, damit der Selbst-Update die neue Version
starten kann.
"""

import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def _name():
    return f"WeintCompanionTest-{uuid.uuid4().hex[:10]}"


def _pump(app, until, seconds=3.0):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        app.processEvents()
        if until():
            return True
        time.sleep(0.01)
    return False


def test_second_start_shows_the_first_and_ends(app):
    from core.single_instance import SingleInstance

    name = _name()
    shown = []
    first = SingleInstance(name)
    assert first.notify_running() is False, "niemand laeuft - trotzdem gemeldet"
    assert first.listen(lambda: shown.append(1))

    # Ein echter zweiter Prozess, wie ein Doppelklick auf das Symbol.
    code = (
        "import os,sys; os.environ.setdefault('QT_QPA_PLATFORM','offscreen');"
        f"sys.path.insert(0, {str(ROOT)!r});"
        "from PySide6.QtCore import QCoreApplication; a = QCoreApplication([]);"
        "from core.single_instance import SingleInstance;"
        f"sys.exit(0 if SingleInstance({name!r}).notify_running() else 3)"
    )
    proc = subprocess.Popen([sys.executable, "-c", code])
    assert _pump(app, lambda: proc.poll() is not None and bool(shown), 10), "zweiter Start nicht angekommen"
    assert proc.returncode == 0, "zweiter Start fand die laufende Companion nicht"
    assert shown == [1], "laufende Companion holte ihr Fenster nicht"

    first.close()


def test_after_close_a_new_start_takes_over(app):
    """Selbst-Update: die alte gibt den Kanal frei, die neue startet."""
    from core.single_instance import SingleInstance

    name = _name()
    first = SingleInstance(name)
    assert first.listen(lambda: None)
    first.close()

    second = SingleInstance(name)
    assert second.notify_running() is False, "nach dem Beenden noch belegt - Update startete nicht"
    assert second.listen(lambda: None), "neue Version kann den Kanal nicht belegen"
    second.close()


def test_name_is_per_user_and_plain():
    from core.single_instance import server_name

    n = server_name()
    assert n.startswith("WeintCompanion-") and n.replace("-", "").isalnum()
    assert server_name() == n


def test_tray_option_is_gone():
    """Die Einstellung "In Tray minimieren" gibt es nicht mehr."""
    for rel in ("gui/pages/settings_sections/general.py", "gui/main_window.py",
                "core/companion_manager.py", "core/config.py"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "minimize_to_tray" not in text, rel
        assert "tray_settings_changed" not in text, rel


def test_close_hides_to_tray_and_quit_releases(app):
    """Kreuz -> Tray (ohne Einstellung); Beenden gibt den Kanal frei."""
    import inspect
    from gui.main_window import MainWindow

    close = inspect.getsource(MainWindow.closeEvent)
    assert "event.ignore()" in close and "self.hide()" in close
    assert "_release_single_instance" in close
    quit_src = inspect.getsource(MainWindow._quit_from_tray)
    assert quit_src.index("_release_single_instance") < quit_src.index("_shutdown_services")
