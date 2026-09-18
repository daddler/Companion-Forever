"""
Die Aufgabenkarte der Übersicht.

Sie ist die Antwort auf die Frage, mit der jemand diese Seite vor dem
Raid öffnet - *muss ich noch was machen?* - und deshalb der Ort, an
dem zwei Fehler besonders teuer wären:

1. **Eine Aufgabe, gegen die sich nichts tun lässt.** Eine Liste, auf
   der Störungen stehen, wird nach dem zweiten Mal nicht mehr gelesen.
2. **Eine leere Liste, die "alles in Ordnung" behauptet, obwohl noch
   nichts geprüft wurde.** Das ist dieselbe Verwechslung wie
   `stars == 0` im Analyzer, nur an der sichtbarsten Stelle der App.
"""

import types

import pytest


def _app():

    pytest.importorskip("PySide6")

    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


class _Config:

    def __init__(self):
        self.data = {}

    def get_accent(self):
        return "violet"

    def get_density(self):
        return "comfortable"

    def get_motion_reduced(self):
        return False


@pytest.fixture
def card():

    _app()

    from gui.theme.theme_manager import init_theme

    init_theme(_Config())

    from gui.widgets.task_card import TaskCard

    widget = TaskCard()

    yield widget

    widget.close()


def _task(key="k", urgency=None, title="Irgendwas", calls=None):

    from gui.widgets.task_card import URGENCY_DUE, Task

    return Task(
        key=key,
        title=title,
        detail="",
        action="Machen",
        on_action=(lambda: calls.append(key)) if calls is not None else (lambda: None),
        urgency=urgency or URGENCY_DUE,
    )


# --------------------------------------------------


def test_an_empty_card_says_so_instead_of_disappearing(card):
    """
    Eine Karte, die im Ruhezustand verschwindet, hinterlässt eine
    Lücke, in der man sich fragt, ob sie etwas verschweigt.
    """

    card.apply([])

    assert not card.empty.isHidden()

    assert card.count.isHidden()


def test_the_count_names_how_many(card):

    card.apply([_task("a"), _task("b")])

    assert card.count.text() == "2"

    assert not card.count.isHidden()

    assert card.empty.isHidden()


def test_blocking_tasks_come_first(card):
    """
    Die Reihenfolge ist eine Eigenschaft der Karte und nicht der
    Seite, die sie füllt - sonst hinge sie daran, in welcher
    Reihenfolge jemand die Zustände abfragt.
    """

    from gui.widgets.task_card import (
        URGENCY_BLOCKING,
        URGENCY_DUE,
        URGENCY_IDLE,
    )

    card.apply([
        _task("c", URGENCY_IDLE, "Kann warten"),
        _task("a", URGENCY_DUE, "Sollte sein"),
        _task("b", URGENCY_BLOCKING, "Muss sein"),
    ])

    titles = [row.title.text() for row in card._rows]

    assert titles == ["Muss sein", "Sollte sein", "Kann warten"]


def test_every_row_carries_a_button_that_does_something(card):
    """
    Der Knopf ist das Aufnahmekriterium: gibt es keinen sinnvollen,
    gehört die Zeile nicht auf diese Karte.
    """

    calls = []

    card.apply([_task("a", calls=calls)])

    row = card._rows[0]

    assert row.button.text() == "Machen"

    row.button.click()

    assert calls == ["a"]


def test_a_second_apply_replaces_the_rows_instead_of_adding(card):
    """
    `refresh()` läuft bei jeder Zustandsänderung. Würden die Zeilen
    dabei angehängt statt ersetzt, stünde nach einer Minute jede
    Aufgabe zwanzigmal da.
    """

    card.apply([_task("a"), _task("b")])

    card.apply([_task("a")])

    assert len(card._rows) == 1

    assert card.count.text() == "1"


def test_an_unchecked_state_is_named_and_not_called_clean(card):

    card.apply([], "")

    assert card.checked.isHidden()

    card.apply([], "ZULETZT GEPRÜFT vor 3 min")

    assert not card.checked.isHidden()

    assert "vor 3 min" in card.checked.text()
