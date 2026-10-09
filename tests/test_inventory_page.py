"""
Die Seite "Bestand" und die Gold-Kachel der Übersicht.

Geprüft wird an echten Widgets (offscreen), weil die Regeln dieser
Seite erst im Bild stehen: "unbekannt" statt einer Null, der
Leerzustand statt einer leeren Tabelle, und dass die Seite die Datei
nicht in `refresh()` liest.
"""

import os
import types

import pytest

pytest.importorskip("PySide6")

from core.inventory import parse_inventory
from core.lua_reader import read_variable

from tests.test_inventory import SAVED


@pytest.fixture(scope="module")
def qt_app():

    from PySide6.QtWidgets import QApplication

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    app = QApplication.instance() or QApplication([])

    from gui.theme.theme_manager import init_theme

    try:
        init_theme(types.SimpleNamespace(data={}, save=lambda: None))

    except Exception:
        pass

    return app


def _manager(wow_path=None):

    return types.SimpleNamespace(
        state=types.SimpleNamespace(wow_path=wow_path, wow_found=True),
        logger=types.SimpleNamespace(warning=lambda *_: None),
    )


def _inventory():

    return parse_inventory(read_variable(SAVED, "WeintCodex_SavedData"))


def test_empty_page_says_why(qt_app):

    from gui.pages.inventory import InventoryPage

    page = InventoryPage(_manager())

    page.refresh()

    assert page.stack.currentIndex() == 0

    assert page.empty.title.text() == "Kein Spielordner gefunden"


def test_filled_page_searches_and_names_unknowns(qt_app):

    from gui.pages.inventory import InventoryPage

    page = InventoryPage(_manager("/nirgends"))

    page._on_loaded(_inventory())

    assert page.stack.currentIndex() == 1

    assert page.header.title.text() == "2 Gegenstände über 2 Charaktere."

    assert "Bank unbekannt" in page.footer.text()

    page.search.setText("leinen")

    assert page.tree.topLevelItemCount() == 1

    top = page.tree.topLevelItem(0)

    assert top.text(1) == "37"

    assert top.childCount() == 2

    page.search.setText("gibtsnicht")

    assert page.tree.topLevelItem(0).text(0) == "Keiner deiner Charaktere hat das."


def test_gold_tile_never_shows_zero_for_unknown(qt_app):

    from core.inventory import Inventory
    from gui.pages.overview import GoldTile

    tile = GoldTile()

    tile.apply(Inventory())

    assert tile.value.text() == "unbekannt"

    tile.apply(_inventory())

    assert tile.value.text() == "123 g 45 s"

    assert "1 ohne Goldstand" in tile.note.text()


def test_inventory_page_refresh_reads_no_file(qt_app, monkeypatch):
    """`refresh()` darf nur zeichnen - gelesen wird in `on_enter()`."""

    import core.inventory as module

    from gui.pages.inventory import InventoryPage

    def boom(*_args, **_kwargs):
        raise AssertionError("refresh() hat die Datei gelesen")

    monkeypatch.setattr(module, "load", boom)

    page = InventoryPage(_manager("/nirgends"))

    page.refresh()
