"""Die Seite "Töne" (gui/pages/sounds.py) - offscreen."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from core import custom_sounds as cs


class _Log:
    def __getattr__(self, _name):
        return lambda *_a, **_k: None


class _State:
    addons_path = None


class _Manager:
    def __init__(self, addons):
        self.state = _State()
        self.state.addons_path = addons
        self.logger = _Log()


class _Config:
    data = {}

    def get(self, key, default=None):
        return default

    def set(self, *_a, **_k):
        pass

    def save(self):
        pass


@pytest.fixture
def page(tmp_path, monkeypatch):

    monkeypatch.setattr(cs, "ffmpeg_path", lambda: None)

    from PySide6.QtWidgets import QApplication

    QApplication.instance() or QApplication([])

    from gui.theme.theme_manager import init_theme

    init_theme(_Config())

    from gui.pages.sounds import SoundsPage

    addons = tmp_path / "AddOns"
    addons.mkdir()

    return SoundsPage(_Manager(addons))


def test_an_empty_page_invites(page):

    assert "Noch kein eigener Ton" in page.header.title.text()
    assert all(not slot.remove.isVisible() for slot in page.slots)


def test_adding_fills_the_first_slot(page, tmp_path):

    src = tmp_path / "gong.ogg"
    src.write_bytes(b"OggS" + b"\0" * 40)

    page.add_file(str(src))

    assert page.slots[0].sound is not None
    assert page.slots[0].name.text() == "gong"
    assert "Ein eigener Ton" in page.header.title.text()
    assert "Platz 1" in page.message.text()


def test_a_refused_file_is_explained(page, tmp_path):

    src = tmp_path / "x.txt"
    src.write_text("nein")

    page.add_file(str(src))

    assert "Format" in page.message.text()
    assert cs.load(page.manager.state.addons_path) == []


def test_without_wow_nothing_can_be_added(page):

    page.manager.state.addons_path = None
    page.refresh()

    assert not page.add_button.isEnabled()
    assert "WoW-Ordner" in page.header.title.text()


def test_trim_selection_never_breaks_the_rules():

    from gui.dialogs.sound_trim import selection

    # Ende über 4 s hinaus gezogen: der Start rückt nach.
    assert selection(1.0, 9.0, 20.0, "end") == (5.0, 9.0)
    # Start hinter das Ende gezogen: das Ende rückt mit.
    assert selection(6.0, 5.0, 20.0, "start") == (6.0, 6.2)
    # Nie über die Datei hinaus.
    assert selection(19.0, 25.0, 20.0, "start") == (19.0, 20.0)


@pytest.mark.skipif(not cs.ffmpeg_path(), reason="ffmpeg fehlt")
def test_trim_dialog_shows_the_file_and_saves_the_choice(tmp_path):

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    from tests.test_custom_sounds import _tone_in_silence
    from gui.dialogs.sound_trim import SoundTrimDialog

    src = _tone_in_silence(tmp_path / "ton.wav")

    dialog = SoundTrimDialog(str(src), cs.ffmpeg_path())

    assert abs(dialog.duration - 8.0) < 0.1 and dialog.peaks
    assert (dialog.start, dialog.end) == (0.0, cs.MAX_SECONDS)

    dialog.start_box.setValue(3.0)
    dialog.end_box.setValue(5.0)

    assert (dialog.start, dialog.end) == (3.0, 5.0)
    assert "2,0" in dialog.length.text()

    dialog.done(0)
    assert app is not None


def test_trim_cursor_tells_what_a_drag_does():

    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    from gui.dialogs.sound_trim import Waveform

    wave = Waveform([0.5] * 100, 10.0)
    wave.resize(1000, 110)
    wave.set_range(2.0, 6.0)   # Kanten bei x = 200 und x = 600

    assert wave.hasMouseTracking()
    assert wave.zone(200) == "start" and wave.zone(604) == "end"
    assert wave.zone(400) == "inside" and wave.zone(800) == "outside"
    assert wave.CURSORS["end"] == Qt.SizeHorCursor
    assert wave.CURSORS["inside"] == Qt.OpenHandCursor

    # Verschieben behält die Länge und bleibt in der Datei.
    moved = []
    wave.dragged.connect(lambda a, b, _m: moved.append((round(a, 2), round(b, 2))))
    wave._anchor = ("move", 2.0)

    class _Ev:
        def __init__(self, x):
            self._x = x

        def position(self):
            from PySide6.QtCore import QPointF
            return QPointF(self._x, 50)

    wave.mouseMoveEvent(_Ev(950))
    assert moved[-1] == (6.0, 10.0)
    assert app is not None
