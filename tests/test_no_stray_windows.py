"""
Kein Widget darf beim Bauen kurz als eigenes Fenster aufgehen.

Der Bericht (Windows 11, 11/2026): die Companion liegt im Tray, der
Spieler spielt über Steam/Epic im Vollbild - und ab und zu blitzt ein
Fenster auf, das sofort wieder weg ist. Das Spiel verliert dabei den
Fokus und fliegt aus dem Vollbild.

Die Ursache: `setVisible(True)` auf einem Widget **ohne Eltern** macht
es zu einem eigenen Fenster der obersten Ebene, bis ein Layout es kurz
danach in seinen Elternteil hängt. Ein Layout ohne eigenes Widget
hängt nichts um, also reichte selbst das `addWidget` davor nicht.
Unter Windows holt sich so ein Fenster den Vordergrund. Die
Übersicht baut ihre Aufgabenzeilen bei jedem `state_changed` neu -
also auch im Tray, alle paar Sekunden.

Geprüft wird jedes Bauteil, das so gebaut war: ohne Eltern erzeugt,
darf beim Bauen kein Fenster außer ihm selbst ein Show-Ereignis
bekommen - und es selbst auch nicht, solange niemand `show()` ruft.
"""

import os

import pytest

pytest.importorskip("PySide6")


@pytest.fixture(scope="module")
def qt_app():

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    from gui.theme.theme_manager import init_theme

    init_theme(app)

    yield app


@pytest.fixture
def shown_windows(qt_app):

    from PySide6.QtCore import QEvent, QObject
    from PySide6.QtWidgets import QWidget

    seen = []

    class Watch(QObject):

        def eventFilter(self, obj, event):

            if (
                event.type() == QEvent.Show
                and isinstance(obj, QWidget)
                and obj.isWindow()
            ):
                seen.append(type(obj).__name__)

            return False

    watch = Watch()

    qt_app.installEventFilter(watch)

    yield seen

    qt_app.removeEventFilter(watch)


def _builders():

    from gui.widgets.chip import Chip
    from gui.widgets.empty_state import EmptyState
    from gui.widgets.task_card import Task, TaskRow
    from gui.widgets.toast import Toast

    task = Task(
        key="k", title="Titel", detail="Mit Erklärung", action="Los",
        on_action=lambda: None,
    )

    return {
        "TaskRow": lambda: TaskRow(task),
        "Chip": lambda: Chip("1 UPDATE", "warn", dot=True),
        "EmptyState": lambda: EmptyState(
            title="Leer", explanation="Nichts da", action="Öffnen",
        ),
        "Toast": lambda: Toast("Erledigt", "ok", "Rückgängig"),
    }


@pytest.mark.parametrize(
    "name", ["TaskRow", "Chip", "EmptyState", "Toast"]
)
def test_building_opens_no_window(qt_app, shown_windows, name):

    widget = _builders()[name]()

    qt_app.processEvents()

    assert shown_windows == [], (
        f"{name} öffnet beim Bauen ein Fenster: {shown_windows}"
    )

    widget.deleteLater()
