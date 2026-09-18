"""
"Was jetzt zu tun ist" - die Handlungskarte der Übersicht.

WARUM ES DIESE KARTE GIBT
-------------------------

Bis 4.0 verteilte sich der Handlungsbedarf der Übersicht auf drei
Stellen: ein Update-Hinweis ganz oben, ein Vorbereitungsring in der
Mitte, eine aufklappbare Systemzeile unten. Jede für sich war
richtig; zusammen beantworteten sie die Frage, die jemand vor dem
Raid tatsächlich stellt - *muss ich noch irgendwas machen?* - an drei
Orten und in drei Formen, und die Antwort "nein" sah aus wie drei
verschiedene Auskünfte.

Hier steht sie einmal, als Liste, in fester Reihenfolge: was den Raid
verhindert, zuerst.

WAS EINE AUFGABE IST
--------------------

Eine Aufgabe ist etwas, das **der Nutzer erledigen kann** - nicht
alles, was gerade nicht in Ordnung ist. "Der Bot ist nicht
erreichbar" ist keine Aufgabe, sondern eine Störung; sie gehört unter
"Verbindungen" und nicht hierher. Der Unterschied ist nicht
kosmetisch: eine Liste, auf der Dinge stehen, gegen die man nichts
tun kann, wird nach dem zweiten Mal nicht mehr gelesen.

Deshalb trägt jede Zeile einen Knopf. Gibt es keinen sinnvollen,
gehört die Zeile nicht auf diese Karte.

DIE LEERE KARTE
---------------

Sie ist der Normalfall und sagt das auch. Eine Karte, die im
Ruhezustand verschwindet, hinterlässt eine Lücke, in der man sich
fragt, ob sie etwas verschweigt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.theme import tokens
from gui.theme.fonts import font
from gui.theme.icons import tinted_pixmap
from gui.theme.restyle import restyle
from gui.theme.theme_manager import theme
from gui.widgets.card import Card
from gui.widgets.eyebrow import eyebrow_label
from gui.widgets.wrapped_label import enable_wrap


#
# Dringlichkeit einer Aufgabe. Sie entscheidet über Reihenfolge,
# Farbe des Symbolfeldes und darüber, ob der Knopf getönt ist.
#
# Drei Stufen und nicht fünf: mehr lassen sich in einer Liste von
# selten mehr als vier Zeilen nicht unterscheiden, und eine
# Abstufung, die niemand sieht, ist eine Behauptung ohne Wirkung.
#

URGENCY_BLOCKING = "blocking"   # ohne das geht der Raid nicht

URGENCY_DUE = "due"             # sollte vor dem Raid erledigt sein

URGENCY_IDLE = "idle"           # kann warten


_ORDER = {
    URGENCY_BLOCKING: 0,
    URGENCY_DUE: 1,
    URGENCY_IDLE: 2,
}


_STATE_KEY = {
    URGENCY_BLOCKING: "warn",
    URGENCY_DUE: "info",
    URGENCY_IDLE: "",
}


@dataclass(frozen=True)
class Task:
    """
    Eine Zeile der Karte.

    `detail` darf leer sein, `action` nicht - siehe Modulkommentar.
    """

    key: str

    title: str

    detail: str

    action: str

    on_action: Callable[[], None]

    urgency: str = URGENCY_DUE

    icon: str = "sync"


class TaskRow(QFrame):
    """
    Eine Aufgabe als Zeile: Symbolfeld, Text, Knopf.
    """

    def __init__(self, task: Task, parent=None):

        super().__init__(parent)

        self._task = task

        self.setObjectName("taskRow")

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            tokens.SPACE[2], tokens.SPACE[2],
            tokens.SPACE[2], tokens.SPACE[2],
        )

        layout.setSpacing(tokens.SPACE[2])

        #
        # Das Symbolfeld. Es trägt die Dringlichkeit als Tönung -
        # nicht der Text, denn eine eingefärbte Überschrift liest sich
        # als Warnung und nicht als Aufgabe.
        #

        self.badge = QLabel()

        self.badge.setFixedSize(32, 32)

        self.badge.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.badge, 0, Qt.AlignTop)

        column = QVBoxLayout()

        column.setContentsMargins(0, 0, 0, 0)

        column.setSpacing(tokens.SPACE[0])

        self.title = QLabel(task.title)

        self.title.setFont(font("card"))

        column.addWidget(self.title)

        self.detail = QLabel(task.detail)

        self.detail.setFont(font("small"))

        enable_wrap(self.detail)

        self.detail.setVisible(bool(task.detail))

        column.addWidget(self.detail)

        self.button = QPushButton(task.action)

        self.button.setCursor(Qt.PointingHandCursor)

        self.button.clicked.connect(task.on_action)

        row = QHBoxLayout()

        row.setContentsMargins(0, tokens.SPACE[0], 0, 0)

        row.setSpacing(0)

        row.addWidget(self.button)

        row.addStretch(1)

        column.addLayout(row)

        layout.addLayout(column, 1)

        #
        # Der Akzent kann sich zur Laufzeit ändern; die Tönung des
        # Symbolfelds hängt an der Dringlichkeit und nicht am Akzent,
        # der Knopf der obersten Zeile aber schon.
        #

        theme().accent_changed.connect(self._apply)

        self._apply()

    # --------------------------------------------------

    def _apply(self, _name: str = ""):

        current = theme()

        state_key = _STATE_KEY.get(self._task.urgency, "")

        if state_key:

            tone = tokens.STATE[state_key]

        else:

            tone = tokens.TEXT["muted"]

        restyle(
            self.badge,
            f"""
            QLabel{{
                background:{tokens.tint(tone, tokens.TINT_SURFACE)};
                border:1px solid {tokens.tint(tone, tokens.TINT_BORDER)};
                border-radius:{tokens.RADIUS["md"]}px;
            }}
            """,
        )

        self.badge.setPixmap(
            tinted_pixmap(self._task.icon, tone, 15)
        )

        restyle(
            self.title,
            f"color:{tokens.TEXT['primary']};background:transparent;",
        )

        restyle(
            self.detail,
            f"color:{tokens.TEXT['muted']};background:transparent;",
        )

        #
        # Der Knopf der blockierenden Aufgabe trägt ihre Farbe, alle
        # anderen bleiben neutral. Zwei getönte Knöpfe nebeneinander
        # heben sich gegenseitig auf.
        #

        if self._task.urgency == URGENCY_BLOCKING:

            restyle(
                self.button,
                f"""
                QPushButton{{
                    background:{tokens.tint(tone, 0.10)};
                    border:1px solid {tokens.tint(tone, tokens.TINT_BORDER)};
                    border-radius:{tokens.RADIUS["sm"]}px;
                    color:{tone};
                    padding:0 12px;
                    min-height:30px;
                    font-weight:600;
                }}
                QPushButton:hover{{
                    background:{tokens.tint(tone, 0.16)};
                }}
                """,
            )

        else:

            restyle(
                self.button,
                f"""
                QPushButton{{
                    background:{tokens.SURFACE["raised"]};
                    border:1px solid {tokens.BORDER["base"]};
                    border-radius:{tokens.RADIUS["sm"]}px;
                    color:{tokens.TEXT["secondary"]};
                    padding:0 12px;
                    min-height:30px;
                }}
                QPushButton:hover{{
                    color:{tokens.TEXT["primary"]};
                    border-color:{current.accent_base()};
                }}
                """,
            )

        #
        # Die oberste Zeile liegt eine Stufe höher als die übrigen -
        # dieselbe Schichtung wie überall, hier als Rangfolge.
        #

        raised = self._task.urgency == URGENCY_BLOCKING

        restyle(
            self,
            f"""
            QFrame#taskRow{{
                background:{
                    tokens.SURFACE_EXTRA["shimmer"] if raised
                    else tokens.SURFACE_EXTRA["toast"]
                };
                border-radius:{tokens.RADIUS["md"]}px;
            }}
            """,
        )


class TaskCard(Card):
    """
    Die Karte selbst: Rubrik, Anzahl, Zeilen, Fusszeile.
    """

    def __init__(self, parent=None):

        super().__init__(parent=parent)

        self._rows: list[TaskRow] = []

        header = QHBoxLayout()

        header.setContentsMargins(0, 0, 0, 0)

        header.setSpacing(tokens.SPACE[1])

        header.addWidget(eyebrow_label("WAS JETZT ZU TUN IST"))

        header.addStretch(1)

        self.count = QLabel("0")

        self.count.setFont(font("mono"))

        self.count.setAlignment(Qt.AlignCenter)

        self.count.setFixedHeight(20)

        self.count.setMinimumWidth(20)

        header.addWidget(self.count)

        self.addLayout(header)

        #
        # Der Behälter der Zeilen. Eigener Container, damit die Karte
        # ihre Zeilen austauschen kann, ohne ihre Rubrik und ihre
        # Fusszeile mit abzureissen.
        #

        self.body = QWidget()

        self.body_layout = QVBoxLayout(self.body)

        self.body_layout.setContentsMargins(0, 0, 0, 0)

        self.body_layout.setSpacing(tokens.SPACE[1])

        self.addWidget(self.body)

        #
        # Der Ruhezustand. Er steht im selben Behälter wie die Zeilen
        # und nicht daneben: so kann nie beides gleichzeitig sichtbar
        # sein.
        #

        self.empty = QLabel(
            "Nichts offen. Alles, was vor dem Raid zu erledigen wäre, "
            "ist erledigt."
        )

        self.empty.setFont(font("small"))

        enable_wrap(self.empty)

        self.body_layout.addWidget(self.empty)

        self.addStretch(1)

        footer = QHBoxLayout()

        footer.setContentsMargins(0, tokens.SPACE[0], 0, 0)

        footer.setSpacing(tokens.SPACE[1])

        self.checked = QLabel("")

        self.checked.setFont(font("micro"))

        footer.addWidget(self.checked)

        footer.addStretch(1)

        self.addLayout(footer)

        theme().accent_changed.connect(self._apply)

        self._apply()

    # --------------------------------------------------

    def _apply(self, _name: str = ""):

        current = theme()

        restyle(
            self.count,
            f"""
            QLabel{{
                background:{tokens.tint(current.accent_base(), tokens.TINT_SURFACE)};
                border:1px solid {tokens.tint(current.accent_base(), tokens.TINT_BORDER)};
                border-radius:10px;
                color:{current.accent_base()};
                padding:0 6px;
            }}
            """,
        )

        restyle(
            self.empty,
            f"color:{tokens.TEXT['muted']};background:transparent;",
        )

        restyle(
            self.checked,
            f"color:{tokens.TEXT['faint']};background:transparent;",
        )

    # --------------------------------------------------

    def apply(self, tasks, checked_text: str = ""):
        """
        Die Karte auf eine Aufgabenliste bringen.

        Sortiert wird hier und nicht beim Aufrufer: die Reihenfolge
        ist eine Eigenschaft der Karte ("was den Raid verhindert,
        zuerst") und keine der Seite, die sie füllt.
        """

        tasks = sorted(
            tasks or [],
            key=lambda task: (_ORDER.get(task.urgency, 9), task.title),
        )

        for row in self._rows:

            self.body_layout.removeWidget(row)

            row.setParent(None)

            row.deleteLater()

        self._rows = []

        for task in tasks:

            row = TaskRow(task)

            self.body_layout.insertWidget(len(self._rows), row)

            self._rows.append(row)

        self.empty.setVisible(not tasks)

        self.count.setText(str(len(tasks)))

        self.count.setVisible(bool(tasks))

        self.checked.setText(checked_text)

        self.checked.setVisible(bool(checked_text))
