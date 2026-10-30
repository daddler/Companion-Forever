"""
Berufe - was deine Charaktere herstellen können, ohne das Spiel zu
starten.

Neu in 1.0.0. Das Addon merkt sich je Charakter die gelernten Rezepte
(aus dem Berufsfenster) und seit 1.0.0.0 die Fertigkeit je Beruf; die
Namen kommen aus dem Bestand des installierten Addons. Gelesen wird
`core/professions.py` in einem Thread aus `on_enter()`, nie aus
`refresh()`.

Zwei Fragen, zwei Hälften: links *wer hat welchen Beruf auf welcher
Stufe*, rechts *wer kann dieses Rezept*. Was nicht bekannt ist, sagt
die Seite: "Stufe unbekannt" statt 0, "Berufsfenster nie offen" statt
"0 Rezepte".

Darunter, seit 1.2.0, die **Aufträge** der Gilde (`core/craft_orders.py`):
was du herstellen sollst und was du bestellt hast, mit Annehmen,
Erledigt, Ablehnen und Stornieren. Der Abschnitt steht außerhalb des
Stapels, damit er auch ohne gemeldete Berufe sichtbar ist. Die Knöpfe
senden in einem eigenen Thread (`set_status_async`), nie aus
`refresh()`.

Seit 1.3.0 ein zweiter Reiter, **Preise** (`core/auction_history.py`):
die Auktionspreise aus den Scans von WeintCodex über Wochen und Monate,
was sich gegenüber der Woche bewegt hat und der Verlauf je Gegenstand.
Eigener Lader, der Archiv liest und schreibt - im Thread, nie in
`refresh()`.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core import auction_history as core_auction
from core import professions as core_professions
from core.professions import Professions
from gui.controllers.saved_loader import SavedDataLoader, auction_loader
from gui.pages._page import Page
from gui.theme import tokens
from gui.theme.fonts import font
from gui.theme.restyle import restyle
from gui.widgets.card import Card
from gui.widgets.empty_state import EmptyState
from gui.widgets.eyebrow import eyebrow_label
from gui.widgets.wrapped_label import enable_wrap


def style_tree(tree: QTreeWidget):
    """Wie auf der Bestandsseite: ohne diese Zeilen zeichnet Qt den Kopf schwarz auf schwarz."""

    tree.setUniformRowHeights(True)

    tree.setFrameShape(QTreeWidget.NoFrame)

    tree.setFont(font("body"))

    restyle(
        tree,
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


def muted_label() -> QLabel:

    label = QLabel("")

    label.setFont(font("small"))

    enable_wrap(label)

    restyle(label, f"color:{tokens.TEXT['muted']};background:transparent;")

    return label


def _loader(manager) -> SavedDataLoader:

    loader = getattr(manager, "_professions_loader", None)

    if loader is None:

        loader = SavedDataLoader(manager, core_professions.load, Professions, "ProfessionsLoad")

        try:
            manager._professions_loader = loader

        except AttributeError:
            pass

    return loader


def change_text(change) -> str:
    """"−12 %" / "+40 %"; ohne Schnitt kein Trend, nie "0 %"."""

    if change is None:
        return "zu wenig Verlauf"

    sign = "+" if change > 0 else ("−" if change < 0 else "±")

    return f"{sign}{abs(change):.0f} %"


class ProfessionsPage(Page):

    def __init__(self, manager, parent=None):

        super().__init__(manager, "BERUFE", "Was deine Charaktere herstellen können.", parent)

        self.loader = _loader(manager)

        self.data = self.loader.result

        self.reload_button = QPushButton("Neu einlesen")

        self.reload_button.setObjectName("secondary")

        self.reload_button.setCursor(Qt.PointingHandCursor)

        self.reload_button.clicked.connect(self._reload)

        self.header.addAction(self.reload_button)

        self.loader.changed.connect(self._on_loaded)

        self.loader.busy.connect(self.reload_button.setDisabled)

        self.auction_loader = auction_loader(manager)

        self.auction = self.auction_loader.result

        self.auction_loader.changed.connect(self._on_auction_loaded)

        #
        # Zwei Reiter: Berufe (mit Aufträgen) und Preise.
        #

        tabs = QHBoxLayout()

        tabs.setSpacing(8)

        self.tab_buttons = []

        for index, text in enumerate(("Berufe & Aufträge", "Preise")):

            button = QPushButton(text)

            button.setObjectName("secondary")

            button.setCheckable(True)

            button.setCursor(Qt.PointingHandCursor)

            button.clicked.connect(lambda _=False, i=index: self._show_tab(i))

            tabs.addWidget(button)

            self.tab_buttons.append(button)

        tabs.addStretch(1)

        self.addLayout(tabs)

        self.tabs = QStackedWidget()

        crafting = QWidget()

        self._crafting = QVBoxLayout(crafting)

        self._crafting.setContentsMargins(0, 0, 0, 0)

        self._crafting.setSpacing(20)

        self.stack = QStackedWidget()

        self.empty = EmptyState("BERUFE", "Noch keine Berufe gemeldet", "", icon="vorbereitung")

        self.stack.addWidget(self.empty)

        content = QWidget()

        row = QHBoxLayout(content)

        row.setContentsMargins(0, 0, 0, 0)

        row.setSpacing(20)

        left = Card()

        left.addWidget(eyebrow_label("CHARAKTERE"))

        self.chars = QTreeWidget()

        self.chars.setColumnCount(3)

        self.chars.setHeaderLabels(["Charakter / Beruf", "Stufe", "Rezepte"])

        self.chars.setMinimumHeight(320)

        style_tree(self.chars)

        head = self.chars.header()

        head.setSectionResizeMode(0, QHeaderView.Stretch)

        head.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        head.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        left.addWidget(self.chars, 1)

        self.footer = muted_label()

        left.addWidget(self.footer)

        row.addWidget(left, 1)

        right = Card()

        right.addWidget(eyebrow_label("WER KANN DAS?"))

        self.search = QLineEdit()

        self.search.setPlaceholderText("Rezeptname oder Zaubernummer")

        self.search.setClearButtonEnabled(True)

        self.search.textChanged.connect(self._apply_search)

        right.addWidget(self.search)

        self.hits = QTreeWidget()

        self.hits.setColumnCount(2)

        self.hits.setHeaderLabels(["Rezept", "Beruf"])

        self.hits.setMinimumHeight(320)

        style_tree(self.hits)

        self.hits.header().setSectionResizeMode(0, QHeaderView.Stretch)

        self.hits.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        right.addWidget(self.hits, 1)

        self.source = muted_label()

        right.addWidget(self.source)

        row.addWidget(right, 1)

        self.stack.addWidget(content)

        self._crafting.addWidget(self.stack, 1)

        self._crafting.addWidget(self._build_orders())

        self.tabs.addWidget(crafting)

        self.tabs.addWidget(self._build_prices())

        self.addWidget(self.tabs, 1)

        self._show_tab(0)

        self._show_empty()

    def _show_tab(self, index: int):

        self.tabs.setCurrentIndex(index)

        for i, button in enumerate(self.tab_buttons):
            button.setChecked(i == index)

    # --------------------------------------------------
    # Preise
    # --------------------------------------------------

    def _build_prices(self) -> QWidget:

        card = Card()

        card.addWidget(eyebrow_label("AUKTIONSPREISE"))

        row = QHBoxLayout()

        row.setSpacing(8)

        self.market_box = QComboBox()

        self.market_box.currentIndexChanged.connect(lambda _=0: self._draw_prices())

        row.addWidget(self.market_box)

        self.price_search = QLineEdit()

        self.price_search.setPlaceholderText("Gegenstand oder Nummer – leer: was sich diese Woche bewegt hat")

        self.price_search.setClearButtonEnabled(True)

        self.price_search.textChanged.connect(lambda _="": self._draw_prices())

        row.addWidget(self.price_search, 1)

        card.addLayout(row)

        self.prices = QTreeWidget()

        self.prices.setColumnCount(4)

        self.prices.setHeaderLabels(["Gegenstand", "Zuletzt", "Schnitt der Woche davor", "Änderung"])

        self.prices.setMinimumHeight(360)

        style_tree(self.prices)

        head = self.prices.header()

        head.setSectionResizeMode(0, QHeaderView.Stretch)

        for column in (1, 2, 3):
            head.setSectionResizeMode(column, QHeaderView.ResizeToContents)

        card.addWidget(self.prices, 1)

        self.prices_note = muted_label()

        card.addWidget(self.prices_note)

        return card

    def _on_auction_loaded(self, data):

        self.auction = data

        current = self.market_box.currentData()

        self.market_box.blockSignals(True)

        self.market_box.clear()

        for market in data.markets:
            self.market_box.addItem(market.label, market.key)

        index = self.market_box.findData(current)

        self.market_box.setCurrentIndex(index if index >= 0 else 0)

        self.market_box.blockSignals(False)

        self.refresh()

    def _draw_prices(self):

        self.prices.clear()

        data = self.auction

        self.market_box.setVisible(len(data.markets) > 1)

        market = data.market(self.market_box.currentData()) if data.markets else None

        if market is None:

            if data.error:
                text = f"Spielstand nicht lesbar ({data.error})."

            else:
                text = (
                    "Noch keine Preise. Schalte im Spiel Komfort → Auktionspreise ein und "
                    "scanne am Auktionshaus; beim Ausloggen schreibt das Spiel die Datei, "
                    "danach sammelt die Companion jeden Tag dazu."
                )

            self.prices_note.setText(text)

            return

        query = self.price_search.text()

        rows = market.search(query) if query.strip() else market.movers()

        for trend in rows:

            average = core_auction.money_text(trend.average) if trend.average is not None else "–"

            top = QTreeWidgetItem([
                trend.label,
                core_auction.money_text(trend.price),
                average,
                change_text(trend.change),
            ])

            for day, price in reversed(trend.history[-30:]):

                when = core_auction.day_date(day).strftime("%d.%m.%Y")

                top.addChild(QTreeWidgetItem([when, core_auction.money_text(price), "", ""]))

            self.prices.addTopLevelItem(top)

        if not rows:

            text = (
                "Nichts gefunden." if query.strip()
                else "Noch kein Gegenstand mit genug Verlauf – dafür braucht es Scans an mindestens drei Tagen."
            )

            self.prices.addTopLevelItem(QTreeWidgetItem([text, "", "", ""]))

        days = len({d for per in market.days.values() for d in per})

        self.prices_note.setText(
            f"{len(market.days):,} Gegenstände an {days} Scan-Tagen. ".replace(",", ".")
            + "Je Tag das günstigste Angebot je Stück aus deinen eigenen Scans – "
            "Preise anderer Spieler zählen nicht. Aufklappen zeigt den Verlauf."
        )

    # --------------------------------------------------
    # Aufträge
    # --------------------------------------------------

    ORDER_BUTTONS = (
        ("accepted", "Annehmen"),
        ("done", "Erledigt"),
        ("declined", "Ablehnen"),
        ("cancelled", "Stornieren"),
    )

    def _build_orders(self) -> Card:

        card = Card()

        card.addWidget(eyebrow_label("AUFTRÄGE"))

        self.orders = QTreeWidget()

        self.orders.setColumnCount(4)

        self.orders.setHeaderLabels(["Auftrag", "Für / bei", "Material", "Status"])

        self.orders.setMinimumHeight(140)

        self.orders.setRootIsDecorated(False)

        style_tree(self.orders)

        head = self.orders.header()

        head.setSectionResizeMode(0, QHeaderView.Stretch)

        for column in (1, 2, 3):
            head.setSectionResizeMode(column, QHeaderView.ResizeToContents)

        self.orders.itemSelectionChanged.connect(self._update_order_buttons)

        card.addWidget(self.orders)

        row = QHBoxLayout()

        row.setSpacing(8)

        self.order_buttons = {}

        for status, text in self.ORDER_BUTTONS:

            button = QPushButton(text)

            button.setObjectName("secondary")

            button.setCursor(Qt.PointingHandCursor)

            button.setEnabled(False)

            button.clicked.connect(lambda _=False, s=status: self._set_order_status(s))

            row.addWidget(button)

            self.order_buttons[status] = button

        row.addStretch(1)

        card.addLayout(row)

        self.orders_note = muted_label()

        card.addWidget(self.orders_note)

        return card

    def _selected_order(self):

        item = self.orders.currentItem()

        return item.data(0, Qt.UserRole) if item is not None else None

    def _update_order_buttons(self):

        order = self._selected_order()

        moves = order.moves() if order is not None else ()

        for status, button in self.order_buttons.items():
            button.setEnabled(status in moves)

    def _set_order_status(self, status: str):

        order = self._selected_order()

        sync = getattr(self.manager, "craft_order_sync", None)

        if order is None or sync is None:
            return

        for button in self.order_buttons.values():
            button.setEnabled(False)

        sync.set_status_async(order.id, status, done=lambda _result: self.manager.state_changed.emit())

    def _draw_orders(self):

        sync = getattr(self.manager, "craft_order_sync", None)

        orders = sync.orders if sync is not None else ()

        selected = self._selected_order()

        self.orders.clear()

        for order in orders:

            who = order.character if order.role == "crafter" else f"bei {order.character}"

            if order.role == "crafter" and order.requester_name:
                who = f"{order.character} · von {order.requester_name}"

            item = QTreeWidgetItem([
                order.title() + (f" – {order.note}" if order.note else ""),
                who,
                "gestellt" if order.mats else "vom Hersteller",
                order.status_label,
            ])

            item.setData(0, Qt.UserRole, order)

            self.orders.addTopLevelItem(item)

            if selected is not None and selected.id == order.id:
                self.orders.setCurrentItem(item)

        if sync is None or not sync.known:
            self.orders_note.setText(
                "Aufträge kommen über die Discord-Anmeldung (Verbindungen)."
            )
        elif not orders:
            self.orders_note.setText(
                "Keine Aufträge. Neue entstehen im Discord: #berufe → Rezept suchen."
            )
        else:
            self.orders_note.setText(
                "Im Spiel erscheinen Aufträge nach dem nächsten Einloggen oder /reload."
            )

        self._update_order_buttons()

    # --------------------------------------------------

    def on_enter(self):

        self.loader.request()

        self.auction_loader.request()

    def _reload(self):

        self.loader.request(force=True)

        self.auction_loader.request(force=True)

    def _on_loaded(self, data):

        self.data = data

        self.refresh()

    # --------------------------------------------------

    def _show_empty(self):

        if not getattr(self.manager.state, "wow_path", None):

            title = "Kein Spielordner gefunden"

            text = (
                "Die Berufe stehen im Spielstand von WeintCodex. Lege unter "
                "Einstellungen den Ordner von World of Warcraft: Forever fest."
            )

        elif self.data.error:

            title = "Spielstand nicht lesbar"

            text = f"WeintCodex.lua konnte nicht gelesen werden. ({self.data.error})"

        else:

            title = "Noch keine Berufe gemeldet"

            text = (
                "WeintCodex merkt sich die Berufe jedes Charakters, sobald du im "
                "Spiel einmal das Berufsfenster öffnest. Erst beim Ausloggen "
                "schreibt das Spiel die Datei."
            )

        self.empty.title.setText(title)

        self.empty.explanation.setText(text)

        self.stack.setCurrentIndex(0)

    def refresh(self):

        self._draw_orders()

        self._draw_prices()

        data = self.data

        if not data.known or not data.characters:

            self._show_empty()

            return

        self.stack.setCurrentIndex(1)

        count = len(data.characters)

        self.header.setTitle(
            "Berufe über " + ("einen Charakter." if count == 1 else f"{count} Charaktere.")
        )

        self.chars.clear()

        unknown_rank = 0

        for character in data.characters:

            top = QTreeWidgetItem([character.label, "", ""])

            for prof in character.professions:

                if prof.rank is None:

                    rank = "unbekannt"

                    unknown_rank += 1

                else:
                    rank = f"{prof.rank} / {prof.max}" if prof.max else str(prof.rank)

                recipes = str(len(prof.known)) if prof.scanned else "Fenster nie offen"

                child = QTreeWidgetItem([prof.name, rank, recipes])

                for spell in sorted(prof.known, key=lambda s: data.recipe_name(s).lower()):
                    child.addChild(QTreeWidgetItem([data.recipe_name(spell) or f"Rezept {spell}", "", ""]))

                top.addChild(child)

            self.chars.addTopLevelItem(top)

            top.setExpanded(True)

        notes = ["Stand des letzten Ausloggens je Charakter."]

        if unknown_rank:
            notes.append(
                "Stufe unbekannt: der Charakter war seit WeintCodex 1.0.0.0 nicht eingeloggt."
            )

        self.footer.setText(" ".join(notes))

        self.source.setText(
            "Rezeptnamen aus dem Bestand des installierten Addons (unbestätigt)."
            if data.catalog
            else "Addon nicht gefunden – Rezepte erscheinen nur als Nummer."
        )

        self._apply_search(self.search.text())

    def _apply_search(self, text: str):

        self.hits.clear()

        if not text.strip():
            return

        rows = self.data.who_can(text)

        for name, prof, chars in rows:

            top = QTreeWidgetItem([name, prof])

            for label in chars:
                top.addChild(QTreeWidgetItem([label, ""]))

            self.hits.addTopLevelItem(top)

            top.setExpanded(True)

        if not rows:
            self.hits.addTopLevelItem(QTreeWidgetItem(["Keiner deiner Charaktere kennt das.", ""]))
