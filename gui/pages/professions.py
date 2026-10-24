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
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from core import professions as core_professions
from core.professions import Professions
from gui.controllers.saved_loader import SavedDataLoader
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
