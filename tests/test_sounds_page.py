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
