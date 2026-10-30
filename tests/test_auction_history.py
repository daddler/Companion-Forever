"""Preisverläufe des Auktionshauses (neu in 1.3.0), ohne Qt."""

from core import auction_history as ah


def pack(price, qty, day, shared=False):

    return price * 10_000_000 + qty * 10_000 + day + (ah.SHARED if shared else 0)


SAVED = {"auction": {"Realm|Alliance": {
    "items": {2770: pack(90, 12, 303), 2771: pack(500, 1, 303, shared=True)},
    "hist": {2770: "299:100,300:110,301:150,302:abc", 2772: "303:40"},
    "names": {2770: "Kupfererz"},
}}}


def test_unpack_matches_addon():

    assert ah.unpack(pack(123456, 7, 300)) == (123456, 7, 300, False)
    assert ah.unpack(pack(5, 0, 12, shared=True)) == (5, 0, 12, True)


def test_parse_keeps_only_own_prices_and_skips_garbage():

    market = ah.parse_saved(SAVED)["Realm|Alliance"]

    assert market["days"][2770] == {299: 100, 300: 110, 301: 150, 303: 90}
    # "von Spielern" ist keine eigene Messung.
    assert 2771 not in market["days"]
    assert market["names"] == {2770: "Kupfererz"}


def test_trend_against_the_week_before():

    archive = ah.merge_into({}, ah.parse_saved(SAVED))

    market = ah.build(archive).market("Realm|Alliance")

    trend = market.trend(2770)

    assert trend.price == 90 and trend.average == 120
    assert round(trend.change) == -25
    assert market.movers()[0].item_id == 2770


def test_too_little_history_is_no_trend_and_no_name_is_a_number():

    market = ah.build(ah.merge_into({}, ah.parse_saved(SAVED))).market("Realm|Alliance")

    trend = market.trend(2772)

    assert trend.average is None and trend.change is None
    assert trend.label == "Gegenstand 2772"
    assert all(t.item_id != 2772 for t in market.movers())


def test_archive_keeps_more_than_the_addon_and_drops_the_oldest(tmp_path):

    path = tmp_path / ah.FILE_NAME

    old = {"Realm|Alliance": {"names": {}, "days": {2770: {10: 70}, 9: {1: 5}}}}

    ah.write_archive(path, old)

    archive = ah.merge_into(ah.read_archive(path), ah.parse_saved(SAVED))

    days = archive["Realm|Alliance"]["days"]

    # Das Addon kennt Tag 10 längst nicht mehr - das Archiv schon.
    assert days[2770][10] == 70 and days[2770][303] == 90

    archive = ah.merge_into(archive, {}, today=400)

    days = archive["Realm|Alliance"]["days"]

    assert 9 not in days
    assert 10 not in days[2770] and days[2770][303] == 90


def test_prices_tab_draws_without_reading_files():

    import os
    import types

    import pytest

    pytest.importorskip("PySide6")

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    from gui.theme.theme_manager import init_theme

    try:
        init_theme(types.SimpleNamespace(data={}, save=lambda: None))

    except Exception:
        pass

    from gui.pages.professions import ProfessionsPage, change_text

    manager = types.SimpleNamespace(state=types.SimpleNamespace(wow_path=None, addon_path=None))

    page = ProfessionsPage(manager)

    page._on_auction_loaded(ah.build(ah.merge_into({}, ah.parse_saved(SAVED))))

    page._show_tab(1)

    first = page.prices.topLevelItem(0)

    assert first.text(0) == "Kupfererz"
    assert first.text(3) == "−25 %"
    assert change_text(None) == "zu wenig Verlauf"

    page.price_search.setText("2772")

    assert page.prices.topLevelItem(0).text(2) == "–"

    assert app is not None


def test_window_collects_prices_without_the_page_at_most_every_six_hours():

    import types

    from gui.main_window import MainWindow

    calls = []

    fake = types.SimpleNamespace(request=lambda: calls.append(1))

    manager = types.SimpleNamespace(state=types.SimpleNamespace(wow_path=None), _auction_loader=fake)

    window = types.SimpleNamespace(manager=manager)

    MainWindow._collect_auction_prices(window)

    assert calls == []  # ohne Spielordner nichts

    manager.state.wow_path = "/wow"

    MainWindow._collect_auction_prices(window)

    MainWindow._collect_auction_prices(window)

    assert calls == [1]

    window._auction_collected_at -= 6 * 3600 + 1

    MainWindow._collect_auction_prices(window)

    assert calls == [1, 1]
