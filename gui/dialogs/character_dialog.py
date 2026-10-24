"""
Einzelansicht eines Charakters und die Auswahl, welche Charaktere die
Companion verfolgt (5.4.0).

Beide schreiben nur über `CharacterStore.set_main()`/`set_tracked()` -
die Entscheidung liegt dort, die Fenster zeigen nur.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.theme import tokens
from gui.theme.fonts import font
from gui.theme.restyle import restyle
from gui.theme.wow_colors import class_color, class_label
from gui.widgets.class_avatar import ClassAvatar
from gui.widgets.eyebrow import eyebrow_label
from gui.widgets.wrapped_label import enable_wrap


def _label(text: str, colour: str, role: str = "body") -> QLabel:

    label = QLabel(text)

    label.setFont(font(role))

    enable_wrap(label)

    restyle(label, f"color:{colour};background:transparent;")

    return label


def _frame(dialog: QDialog, title: str):

    dialog.setWindowTitle(title)

    dialog.setModal(True)

    dialog.setAttribute(Qt.WA_StyledBackground, True)

    dialog.setStyleSheet(
        f"QDialog{{background:{tokens.SURFACE['card']};}}"
    )

    root = QVBoxLayout(dialog)

    root.setContentsMargins(28, 24, 28, 20)

    root.setSpacing(tokens.SPACE[2])

    return root


class CharacterDialog(QDialog):

    def __init__(self, sheet: dict, store, parent=None):

        super().__init__(parent)

        self.sheet = sheet

        self.store = store

        self.resize(520, 560)

        root = _frame(self, sheet.get("name", "Charakter"))

        head = QHBoxLayout()

        head.setSpacing(tokens.SPACE[2])

        head.addWidget(ClassAvatar(sheet.get("class", ""), 64), alignment=Qt.AlignTop)

        titles = QVBoxLayout()

        titles.addWidget(_label(
            sheet.get("name", ""), class_color(sheet.get("class", "")), "title",
        ))

        parts = [
            sheet.get("spec", ""),
            class_label(sheet.get("class", "")) or "Unbekannte Klasse",
            sheet.get("realm", ""),
        ]

        titles.addWidget(_label(
            " · ".join(p for p in parts if p), tokens.TEXT["secondary"], "small",
        ))

        level = sheet.get("level") or "-"

        item_level = sheet.get("item_level_equipped") or 0.0

        titles.addWidget(_label(
            f"Stufe {level} · Gegenstandsstufe "
            f"{f'{item_level:.0f}' if item_level > 0 else 'unbekannt'}",
            tokens.TEXT["primary"],
        ))

        head.addLayout(titles, 1)

        root.addLayout(head)

        #
        # Inhalt in einer Rolle: Hinweise, dann Ausrüstung.
        #

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setFrameShape(QScrollArea.NoFrame)

        body = QWidget()

        column = QVBoxLayout(body)

        column.setContentsMargins(0, tokens.SPACE[2], 0, 0)

        column.setSpacing(tokens.SPACE[1])

        issues = sorted(sheet.get("issues") or [], key=lambda i: i.get("priority", 9))

        column.addWidget(eyebrow_label(f"HINWEISE ({len(issues)})"))

        if issues:

            for issue in issues:
                column.addWidget(_label(
                    f"• {issue.get('text', '')}", tokens.STATE_TEXT["warn"],
                ))

        elif sheet.get("slots"):

            column.addWidget(_label("Alles angelegt, nichts zerbrochen.", tokens.STATE_TEXT["ok"]))

        else:

            column.addWidget(_label(
                "Das Addon hat für diesen Charakter keine Ausrüstung "
                "gemeldet - geprüft ist also nichts.",
                tokens.TEXT["muted"],
            ))

        slots = sheet.get("slots") or []

        if slots:

            column.addSpacing(tokens.SPACE[2])

            column.addWidget(eyebrow_label("AUSRÜSTUNG"))

            for slot in sorted(slots, key=lambda s: s.get("slot_id", 0)):

                item = slot.get("item") or "leer"

                ilvl = slot.get("item_level") or 0

                row = QHBoxLayout()

                row.addWidget(_label(slot.get("slot", ""), tokens.TEXT["muted"], "small"), 2)

                row.addWidget(_label(
                    item,
                    tokens.TEXT["primary"] if slot.get("item") else tokens.TEXT["faint"],
                    "small",
                ), 5)

                row.addWidget(_label(str(ilvl) if ilvl else "", tokens.TEXT["secondary"], "small"), 1)

                column.addLayout(row)

        column.addStretch(1)

        scroll.setWidget(body)

        root.addWidget(scroll, 1)

        #
        # Handlungen
        #

        buttons = QHBoxLayout()

        self.main_button = QPushButton()

        self.main_button.setCursor(Qt.PointingHandCursor)

        self.main_button.clicked.connect(self._toggle_main)

        buttons.addWidget(self.main_button)

        self.track_button = QPushButton()

        self.track_button.setObjectName("secondary")

        self.track_button.setCursor(Qt.PointingHandCursor)

        self.track_button.clicked.connect(self._toggle_tracked)

        buttons.addWidget(self.track_button)

        buttons.addStretch(1)

        close = QPushButton("Schließen")

        close.setObjectName("ghost")

        close.clicked.connect(self.accept)

        buttons.addWidget(close)

        root.addLayout(buttons)

        self._apply()

    def _apply(self):

        main = self.store.is_main(self.sheet)

        self.main_button.setText("Main entfernen" if main else "★ Als Main markieren")

        tracked = self.store.is_tracked(self.sheet)

        self.track_button.setText("Nicht mehr verfolgen" if tracked else "Wieder verfolgen")

    def _toggle_main(self):

        self.store.set_main(None if self.store.is_main(self.sheet) else self.sheet)

        self._apply()

    def _toggle_tracked(self):

        tracked = self.store.is_tracked(self.sheet)

        self.store.set_tracked(self.sheet, not tracked)

        if tracked:
            self.accept()
        else:
            self._apply()


class TrackingDialog(QDialog):
    """
    Welche Charaktere die Companion zeigt und an den Bot meldet - und
    welcher der Main ist. Gelöscht wird nichts: ein abgewählter
    Charakter bleibt gespeichert und kommt mit einem Haken zurück.
    """

    def __init__(self, store, parent=None):

        super().__init__(parent)

        self.store = store

        self.resize(560, 600)

        root = _frame(self, "Charaktere verwalten")

        root.addWidget(_label("Charaktere verwalten", tokens.WHITE, "title"))

        root.addWidget(_label(
            "Haken weg: der Charakter verschwindet aus der Liste und wird "
            "nicht mehr an den Bot gemeldet. Gespeichert bleibt er - ein "
            "Haken holt ihn zurück. Der Stern macht ihn zum Main; der "
            "steht immer zuerst.",
            tokens.TEXT["secondary"], "small",
        ))

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setFrameShape(QScrollArea.NoFrame)

        body = QWidget()

        column = QVBoxLayout(body)

        column.setContentsMargins(0, 0, 0, 0)

        column.setSpacing(tokens.SPACE[1])

        self.mains = QButtonGroup(self)

        self.mains.setExclusive(False)

        self.rows = []

        sheets = sorted(
            store.own_characters(),
            key=lambda s: (-(s.get("level") or 0), (s.get("name") or "").lower()),
        )

        if not sheets:
            column.addWidget(_label("Noch kein Charakter gemeldet.", tokens.TEXT["muted"]))

        for sheet in sheets:

            row = QHBoxLayout()

            check = QCheckBox(
                f"{sheet.get('name', '')}  ·  Stufe {sheet.get('level') or '?'}"
                + (f"  ·  {sheet.get('realm')}" if sheet.get("realm") else "")
            )

            check.setChecked(store.is_tracked(sheet))

            restyle(check, f"color:{class_color(sheet.get('class', ''))};")

            check.toggled.connect(lambda on, s=sheet: self._tracked(s, on))

            row.addWidget(check, 1)

            star = QRadioButton("Main")

            star.setChecked(store.is_main(sheet))

            self.mains.addButton(star)

            star.toggled.connect(lambda on, s=sheet, b=star: self._main(s, on, b))

            row.addWidget(star)

            column.addLayout(row)

            self.rows.append((sheet, check, star))

        column.addStretch(1)

        scroll.setWidget(body)

        root.addWidget(scroll, 1)

        buttons = QHBoxLayout()

        none = QPushButton("Alle abwählen")

        none.setObjectName("ghost")

        none.clicked.connect(lambda: self._all(False))

        buttons.addWidget(none)

        every = QPushButton("Alle auswählen")

        every.setObjectName("ghost")

        every.clicked.connect(lambda: self._all(True))

        buttons.addWidget(every)

        buttons.addStretch(1)

        done = QPushButton("Fertig")

        done.clicked.connect(self.accept)

        buttons.addWidget(done)

        root.addLayout(buttons)

    def _all(self, on: bool):

        for _sheet, check, _star in self.rows:
            check.setChecked(on)

    def _tracked(self, sheet: dict, on: bool):

        self.store.set_tracked(sheet, on)

        if not on:
            for s, _check, star in self.rows:
                if s is sheet and star.isChecked():
                    star.blockSignals(True)
                    star.setChecked(False)
                    star.blockSignals(False)

    def _main(self, sheet: dict, on: bool, button):

        if on:

            for s, check, star in self.rows:

                if star is not button and star.isChecked():
                    star.blockSignals(True)
                    star.setChecked(False)
                    star.blockSignals(False)

                if s is sheet and not check.isChecked():
                    check.blockSignals(True)
                    check.setChecked(True)
                    check.blockSignals(False)

            self.store.set_main(sheet)

        elif self.store.is_main(sheet):

            self.store.set_main(None)
