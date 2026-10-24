"""
Addon-Fehler - was WeintCodex im Spiel gefangen hat, zum Kopieren.

Neu in 1.0.0. Liest `core/addon_errors.py` in einem Thread aus
`on_enter()`. "Kopieren" legt den Bericht in derselben Form in die
Zwischenablage, die das Addon mit `/wcui fehler` zeigt - fertig zum
Weiterschicken an den Entwickler.

Die Liste wird hier nie gelöscht: die Datei gehört dem Spiel, und
`upsert_variable()` bleibt die eine Stelle, an der die App hineinschreibt.
Leeren geht im Spiel.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
    QVBoxLayout,
)

from core import addon_errors as core_errors
from core.addon_errors import AddonErrors, report
from gui.controllers.saved_loader import SavedDataLoader
from gui.pages._page import Page
from gui.pages.professions import muted_label, style_tree
from gui.widgets.card import Card
from gui.widgets.empty_state import EmptyState
from gui.widgets.eyebrow import eyebrow_label


def _loader(manager) -> SavedDataLoader:

    loader = getattr(manager, "_addon_errors_loader", None)

    if loader is None:

        loader = SavedDataLoader(manager, core_errors.load, AddonErrors, "AddonErrorsLoad")

        try:
            manager._addon_errors_loader = loader

        except AttributeError:
            pass

    return loader


class AddonErrorsPage(Page):

    def __init__(self, manager, parent=None):

        super().__init__(manager, "ADDON-FEHLER", "Was WeintCodex im Spiel gefangen hat.", parent)

        self.loader = _loader(manager)

        self.data = self.loader.result

        self.copy_button = QPushButton("Alle kopieren")

        self.copy_button.setCursor(Qt.PointingHandCursor)

        self.copy_button.clicked.connect(self._copy_all)

        self.header.addAction(self.copy_button)

        self.reload_button = QPushButton("Neu einlesen")

        self.reload_button.setObjectName("secondary")

        self.reload_button.setCursor(Qt.PointingHandCursor)

        self.reload_button.clicked.connect(self._reload)

        self.header.addAction(self.reload_button)

        self.loader.changed.connect(self._on_loaded)

        self.loader.busy.connect(self.reload_button.setDisabled)

        self.stack = QStackedWidget()

        self.empty = EmptyState("ADDON-FEHLER", "Keine Fehler gemeldet", "", icon="changelog")

        self.stack.addWidget(self.empty)

        content = QWidget()

        column = QVBoxLayout(content)

        column.setContentsMargins(0, 0, 0, 0)

        card = Card()

        card.addWidget(eyebrow_label("GEFANGENE FEHLER"))

        self.tree = QTreeWidget()

        self.tree.setColumnCount(4)

        self.tree.setHeaderLabels(["Fehler", "Anzahl", "Zuletzt", "Fassung"])

        self.tree.setMinimumHeight(320)

        style_tree(self.tree)

        head = self.tree.header()

        head.setSectionResizeMode(0, QHeaderView.Stretch)

        for i in (1, 2, 3):
            head.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        card.addWidget(self.tree, 1)

        row = QWidget()

        buttons = QHBoxLayout(row)

        buttons.setContentsMargins(0, 0, 0, 0)

        self.copy_one = QPushButton("Markierten kopieren")

        self.copy_one.setObjectName("secondary")

        self.copy_one.setCursor(Qt.PointingHandCursor)

        self.copy_one.clicked.connect(self._copy_selected)

        buttons.addWidget(self.copy_one)

        buttons.addStretch(1)

        card.addWidget(row)

        self.footer = muted_label()

        card.addWidget(self.footer)

        column.addWidget(card, 1)

        self.stack.addWidget(content)

        self.addWidget(self.stack, 1)

        self._show_empty()

    # --------------------------------------------------

    def on_enter(self):

        self.loader.request()

    def _reload(self):

        self.loader.request(force=True)

    def _on_loaded(self, data):

        self.data = data

        self.refresh()

    # --------------------------------------------------

    def _show_empty(self):

        if not getattr(self.manager.state, "wow_path", None):

            title, text = (
                "Kein Spielordner gefunden",
                "Die Fehler stehen im Spielstand von WeintCodex. Lege unter "
                "Einstellungen den Ordner von World of Warcraft: Forever fest.",
            )

        elif self.data.error:

            title, text = (
                "Spielstand nicht lesbar",
                f"WeintCodex.lua konnte nicht gelesen werden. ({self.data.error})",
            )

        elif not self.data.known:

            title, text = (
                "Noch kein Spielstand",
                "WeintCodex hat noch nichts gespeichert. Erst beim Ausloggen "
                "schreibt das Spiel die Datei.",
            )

        else:

            title, text = (
                "Keine Fehler gemeldet",
                "WeintCodex hat beim letzten Ausloggen keinen eigenen Fehler "
                "gespeichert.",
            )

        self.empty.title.setText(title)

        self.empty.explanation.setText(text)

        self.stack.setCurrentIndex(0)

        self.copy_button.setEnabled(False)

    def refresh(self):

        errors = self.data.errors

        if not errors:

            self._show_empty()

            return

        self.stack.setCurrentIndex(1)

        self.copy_button.setEnabled(True)

        self.header.setTitle(
            "Ein Fehler gespeichert." if len(errors) == 1 else f"{len(errors)} Fehler gespeichert."
        )

        self.tree.clear()

        for index, e in enumerate(errors):

            top = QTreeWidgetItem([f"{e.kind_label}: {e.headline}", str(e.count), e.last or "?", e.version or "?"])

            top.setData(0, Qt.UserRole, index)

            top.setToolTip(0, e.message)

            for line in (e.message.splitlines()[1:] + e.stack.splitlines()):

                child = QTreeWidgetItem([line, "", "", ""])

                child.setFont(0, self.tree.font())

                top.addChild(child)

            self.tree.addTopLevelItem(top)

        self.footer.setText(
            "Stand des letzten Ausloggens. Gelöscht wird die Liste im Spiel; "
            "Spielversion, Klasse und Zone kennt nur der laufende Client und "
            "stehen deshalb nicht im Bericht."
        )

    # --------------------------------------------------

    def _copy(self, errors):

        if errors:
            QGuiApplication.clipboard().setText(report(errors))

    def _copy_all(self):

        self._copy(self.data.errors)

    def _copy_selected(self):

        item = self.tree.currentItem()

        while item is not None and item.parent() is not None:
            item = item.parent()

        if item is None:
            return

        index = item.data(0, Qt.UserRole)

        if isinstance(index, int) and 0 <= index < len(self.data.errors):
            self._copy([self.data.errors[index]])
