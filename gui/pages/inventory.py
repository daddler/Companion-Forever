"""
Bestand - was deine Charaktere haben, ohne das Spiel zu starten.

Neu in 5.1 (Forever-Umbau). Das Addon merkt sich seit 6.24.0.0 je
Charakter Taschen, Ausrüstung, Bank und Gold; im Spiel zeigt es das im
Tooltip und auf seiner Seite "Taschen". Hier steht dasselbe auf dem
Desktop - für die Frage, die man sich vor dem Einloggen stellt: *wer
hat noch Leinenstoff*, *auf welchem Twink liegt der Trank*, *wie viel
Gold habe ich insgesamt*.

Gelesen wird `core/inventory.py`, und zwar:

* **in einem Hintergrund-Thread aus `on_enter()`** und auf Knopfdruck,
  nie aus `refresh()` - der Spielstand kann mit den Auktionspreisen
  mehrere Megabyte haben, und `refresh()` darf nur zeichnen;
* **nur, wenn sich eine Datei geändert hat** (Zeitstempel und Größe).

Was die Seite über ihre Daten sagt, statt es zu verschweigen:
"Stand des letzten Ausloggens" im Kopf, "Bank unbekannt" statt 0 und
die Charaktere ohne Goldstand gezählt neben der Summe.
"""

from __future__ import annotations

import time

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.inventory import Inventory, money_text
from gui.controllers.inventory_loader import inventory_loader
from gui.pages._page import Page
from gui.theme import tokens
from gui.theme.fonts import font
from gui.theme.restyle import restyle
from gui.theme.wow_colors import class_color
from gui.widgets.card import Card
from gui.widgets.empty_state import EmptyState
from gui.widgets.eyebrow import eyebrow_label
from gui.widgets.wrapped_label import enable_wrap


def _ago(at: int) -> str:

    if not at:
        return "unbekannt"

    seconds = max(0, int(time.time() - at))

    if seconds < 3600:
        return f"vor {max(1, seconds // 60)} min"

    if seconds < 86400:
        return f"vor {seconds // 3600} Std"

    days = seconds // 86400

    return "vor 1 Tag" if days == 1 else f"vor {days} Tagen"


class GoldCard(Card):
    """
    Gold über alle Charaktere - wie der Tooltip am Gold im Addon.
    """

    def __init__(self, parent=None):

        super().__init__(parent=parent)

        self.setMinimumWidth(280)

        self.setMaximumWidth(340)

        self.addWidget(eyebrow_label("GOLD"))

        self.total = QLabel("–")

        self.total.setFont(font("displayCard"))

        restyle(self.total, f"color:{tokens.WHITE};background:transparent;")

        self.addWidget(self.total)

        self.note = QLabel("")

        self.note.setFont(font("small"))

        enable_wrap(self.note)

        restyle(self.note, f"color:{tokens.TEXT['muted']};background:transparent;")

        self.addWidget(self.note)

        self.addSpacing(tokens.SPACE[2])

        self.rows = QVBoxLayout()

        self.rows.setContentsMargins(0, 0, 0, 0)

        self.rows.setSpacing(6)

        self.addLayout(self.rows)

        self.addStretch(1)

    def apply(self, inventory: Inventory):

        while self.rows.count():

            item = self.rows.takeAt(0)

            if item.widget() is not None:
                item.widget().deleteLater()

        total, unknown = inventory.gold()

        counted = len(inventory.characters) - unknown

        self.total.setText(money_text(total) if counted else "unbekannt")

        notes = []

        if counted:
            notes.append(
                "über einen Charakter" if counted == 1
                else f"über {counted} Charaktere"
            )

        if unknown:
            notes.append(
                f"{unknown} ohne Goldstand – einmal einloggen"
                if unknown > 1
                else "einer ohne Goldstand – einmal einloggen"
            )

        self.note.setText(", ".join(notes))

        known = [c for c in inventory.characters if c.money is not None]

        known.sort(key=lambda c: -c.money)

        for character in known:

            row = QHBoxLayout()

            row.setContentsMargins(0, 0, 0, 0)

            name = QLabel(character.label)

            name.setFont(font("body"))

            restyle(
                name,
                f"color:{class_color(character.class_token)};"
                "background:transparent;",
            )

            amount = QLabel(money_text(character.money))

            amount.setFont(font("mono"))

            restyle(amount, f"color:{tokens.TEXT['primary']};background:transparent;")

            row.addWidget(name, 1)

            row.addWidget(amount)

            holder = QWidget()

            holder.setLayout(row)

            self.rows.addWidget(holder)


class InventoryPage(Page):

    def __init__(self, manager, parent=None):

        super().__init__(
            manager,
            "BESTAND",
            "Was deine Charaktere haben.",
            parent,
        )

        self.loader = inventory_loader(manager)

        self.inventory = self.loader.inventory

        self.reload_button = QPushButton("Neu einlesen")

        self.reload_button.setObjectName("secondary")

        self.reload_button.setCursor(Qt.PointingHandCursor)

        self.reload_button.clicked.connect(self._reload)

        self.header.addAction(self.reload_button)

        #
        # Gebundene Methoden, keine Lambdas: der Lader lebt so lange
        # wie der Manager, und ein Lambda hielte die Seite fest.
        #

        self.loader.changed.connect(self._on_loaded)

        self.loader.busy.connect(self.reload_button.setDisabled)

        self.stack = QStackedWidget()

        self.empty = EmptyState(
            "BESTAND",
            "Noch kein Bestand gemeldet",
            "",
            icon="charaktere",
        )

        self.stack.addWidget(self.empty)

        content = QWidget()

        row = QHBoxLayout(content)

        row.setContentsMargins(0, 0, 0, 0)

        row.setSpacing(20)

        self.gold = GoldCard()

        row.addWidget(self.gold, 0, Qt.AlignTop)

        search_card = Card()

        search_card.addWidget(eyebrow_label("GEGENSTAND SUCHEN"))

        self.search = QLineEdit()

        self.search.setPlaceholderText("Name oder Gegenstandsnummer, z. B. Leinenstoff")

        self.search.setClearButtonEnabled(True)

        self.search.textChanged.connect(self._apply_search)

        search_card.addWidget(self.search)

        self.tree = QTreeWidget()

        self.tree.setColumnCount(3)

        self.tree.setHeaderLabels(["Gegenstand", "Anzahl", "Wo"])

        self.tree.setRootIsDecorated(True)

        self.tree.setUniformRowHeights(True)

        self.tree.setMinimumHeight(320)

        self.tree.setFrameShape(QTreeWidget.NoFrame)

        self.tree.setFont(font("body"))

        #
        # Das globale Stylesheet kennt keine Baumansicht und keinen
        # Spaltenkopf - ohne diese Zeilen zeichnet Qt den Kopf in der
        # Systemfarbe, auf dunklem Grund schwarz auf schwarz.
        #

        restyle(
            self.tree,
            f"""
            QTreeWidget{{
                background:transparent;
                color:{tokens.TEXT['primary']};
                border:none;
                outline:none;
            }}
            QTreeWidget::item{{
                padding:3px 0;
            }}
            QTreeWidget::item:selected{{
                background:{tokens.SURFACE['raised']};
                color:{tokens.WHITE};
            }}
            QHeaderView::section{{
                background:transparent;
                color:{tokens.TEXT['muted']};
                border:none;
                border-bottom:1px solid {tokens.SURFACE['raised']};
                padding:4px 6px 6px 0;
            }}
            """,
        )

        header = self.tree.header()

        header.setSectionResizeMode(0, QHeaderView.Stretch)

        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        search_card.addWidget(self.tree, 1)

        self.footer = QLabel("")

        self.footer.setFont(font("small"))

        enable_wrap(self.footer)

        restyle(self.footer, f"color:{tokens.TEXT['muted']};background:transparent;")

        search_card.addWidget(self.footer)

        row.addWidget(search_card, 1)

        self.stack.addWidget(content)

        self.addWidget(self.stack, 1)

        self._show_empty()

    # --------------------------------------------------
    # Lesen
    # --------------------------------------------------

    def on_enter(self):

        self.loader.request()

    def _reload(self):

        self.loader.request(force=True)

    def _on_loaded(self, inventory):

        self.inventory = inventory

        self.refresh()

    # --------------------------------------------------
    # Zeichnen
    # --------------------------------------------------

    def _show_empty(self):

        state = self.manager.state

        if not getattr(state, "wow_path", None):

            title = "Kein Spielordner gefunden"

            text = (
                "Der Bestand steht im Spielstand von WeintCodex. Lege unter "
                "Einstellungen den Ordner von World of Warcraft: Forever fest."
            )

        elif self.inventory.error:

            title = "Spielstand nicht lesbar"

            text = (
                "WeintCodex.lua konnte nicht gelesen werden. Meist hilft es, "
                "sich im Spiel einmal ab- und wieder anzumelden. "
                f"({self.inventory.error})"
            )

        else:

            title = "Noch kein Bestand gemeldet"

            text = (
                "WeintCodex merkt sich ab Fassung 6.24 Taschen, Bank und Gold "
                "jedes Charakters. Melde dich im Spiel einmal an und wieder ab "
                "– erst beim Ausloggen schreibt das Spiel die Datei."
            )

        self.empty.title.setText(title)

        self.empty.explanation.setText(text)

        self.stack.setCurrentIndex(0)

        self.header.setTitle("Was deine Charaktere haben.")

    def refresh(self):

        inventory = self.inventory

        if not inventory.known or not inventory.characters:

            self._show_empty()

            return

        self.stack.setCurrentIndex(1)

        count = len(inventory.characters)

        self.header.setTitle(
            f"{len(inventory.item_ids())} Gegenstände über "
            + ("einen Charakter." if count == 1 else f"{count} Charaktere.")
        )

        newest = max((c.at for c in inventory.characters), default=0)

        self.header.setEyebrow(f"BESTAND · STAND {_ago(newest).upper()}")

        self.gold.apply(inventory)

        notes = ["Stand des letzten Ausloggens je Charakter – während du spielst, ändert sich hier nichts."]

        unknown = inventory.bank_unknown()

        if unknown:
            notes.append(
                ("Bei einem Charakter" if unknown == 1 else f"Bei {unknown} Charakteren")
                + " ist die Bank unbekannt: sie war seit dem Einschalten nie offen."
            )

        notes.append("Post und Auktionen kennt der Bestand nicht.")

        self.footer.setText(" ".join(notes))

        self._apply_search(self.search.text())

    def _apply_search(self, text: str):

        self.tree.clear()

        items = self.inventory.search(text)

        for stock in items:

            name = stock.name or f"Gegenstand {stock.item_id}"

            top = QTreeWidgetItem([name, str(stock.total), f"{len(stock.holders)} Charakter" + ("" if len(stock.holders) == 1 else "e")])

            top.setToolTip(0, f"Gegenstandsnummer {stock.item_id}")

            for holder in stock.holders:

                child = QTreeWidgetItem([holder.character.label, str(holder.total), holder.where()])

                child.setForeground(
                    0, QColor(class_color(holder.character.class_token))
                )

                if holder.character.bank is None:
                    child.setToolTip(2, "Bank unbekannt – war nie offen")

                top.addChild(child)

            self.tree.addTopLevelItem(top)

            if text.strip():
                top.setExpanded(True)

        if not items and text.strip():

            self.tree.addTopLevelItem(QTreeWidgetItem([
                "Keiner deiner Charaktere hat das.", "", "",
            ]))
