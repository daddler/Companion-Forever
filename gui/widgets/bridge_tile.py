"""
"Brücken" - die Kachel der Übersicht, die zeigt, was zwischen Addon,
App und Bot tatsächlich läuft.

SIE IST EINE AUSKUNFT, KEINE HANDLUNG
-------------------------------------

Das ist der Unterschied zur Aufgabenkarte daneben
(`gui/widgets/task_card.py`), und er entscheidet darüber, was hier
stehen darf: Zeilen ohne Knopf. Wer wissen will, warum eine Brücke
aus ist, geht auf "Verbindungen" - dort steht, was zuletzt versucht
wurde und woran es hing.

Die Vorgängerin war eine aufklappbare Systemzeile über die volle
Breite der Seite, die sich nur bei Handlungsbedarf öffnete. Zwei
Probleme: sie war im Ruhezustand vier graue Punkte ohne Text, und im
Handlungsfall wiederholte sie, was die Update-Karte schon sagte.

DREI ZUSTÄNDE, NICHT ZWEI
-------------------------

`ok`, `warn` und - der wichtige - **`empty`**: ein Punkt ohne Füllung,
nur als Kontur. Er heisst "darüber ist nichts bekannt" und nicht
"aus". Beim Start ist der Abruf noch unterwegs; ein grauer Punkt sähe
dort aus wie eine Antwort, die niemand gegeben hat. Dieselbe Linie
wie `stars == 0` und `at == -1` im übrigen Projekt.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from gui.theme import tokens
from gui.theme.fonts import font
from gui.theme.restyle import restyle
from gui.theme.theme_manager import theme
from gui.widgets.card import Card
from gui.widgets.eyebrow import eyebrow_label
from gui.widgets.status_dot import StatusDot


#
# Die Beschriftung je Zustand. Sie steht rechts und in Monospace,
# damit die drei Zeilen eine Flucht bilden - eine Kachel, in der drei
# Wörter verschieden weit rechts enden, liest sich als Liste und nicht
# als Zustandsanzeige.
#

STATE_TEXTS = {
    "ok": "AKTIV",
    "warn": "STÖRUNG",
    "empty": "AUS",
}


class BridgeRow(QWidget):

    def __init__(self, label: str, parent=None):

        super().__init__(parent)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.setSpacing(tokens.SPACE[1])

        self.dot = StatusDot("empty")

        layout.addWidget(self.dot, 0, Qt.AlignVCenter)

        self.label = QLabel(label)

        self.label.setFont(font("small"))

        layout.addWidget(self.label, 1)

        self.value = QLabel(STATE_TEXTS["empty"])

        self.value.setFont(font("micro"))

        layout.addWidget(self.value, 0, Qt.AlignVCenter)

        self._state = "empty"

        self._apply()

    # --------------------------------------------------

    def setState(self, state: str, text: str = ""):

        self._state = state if state in STATE_TEXTS else "empty"

        self.dot.setState(self._state)

        self.value.setText(text or STATE_TEXTS[self._state])

        self._apply()

    def _apply(self):

        if self._state == "ok":
            colour = tokens.STATE_TEXT["ok"]

        elif self._state == "warn":
            colour = tokens.STATE_TEXT["warn"]

        else:
            colour = tokens.TEXT["faint"]

        restyle(
            self.label,
            f"""color:{
                tokens.TEXT["secondary"] if self._state != "empty"
                else tokens.TEXT["muted"]
            };background:transparent;""",
        )

        restyle(
            self.value,
            f"color:{colour};background:transparent;",
        )


class BridgeTile(Card):
    """
    Drei Brücken und der Zeitpunkt des letzten Abgleichs.
    """

    def __init__(self, parent=None):

        super().__init__(parent=parent)

        self.addWidget(eyebrow_label("BRÜCKEN"))

        column = QVBoxLayout()

        column.setContentsMargins(0, 0, 0, 0)

        column.setSpacing(tokens.SPACE[1])

        self.rows = {
            "addon": BridgeRow("Addon im Spiel"),
            "discord": BridgeRow("Gilden-Kalender"),
            "roster": BridgeRow("Charakter-Roster"),
        }

        for row in self.rows.values():
            column.addWidget(row)

        self.addLayout(column)

        self.addStretch(1)

        self.synced = QLabel("")

        self.synced.setFont(font("micro"))

        self.addWidget(self.synced)

        theme().accent_changed.connect(self._apply)

        self._apply()

    # --------------------------------------------------

    def _apply(self, _name: str = ""):

        restyle(
            self.synced,
            f"color:{tokens.TEXT['faint']};background:transparent;",
        )

    # --------------------------------------------------

    def apply(self, state, last_sync: str = ""):
        """
        `state` ist der `AppState` des CompanionManagers.

        Bewusst **kein** eigener Abruf: eine Kachel, die selbst ins
        Netz greift, liefe in der Neuzeichnungsschleife der Seite mit
        (siehe docs/architecture/navigation.md).
        """

        self.rows["addon"].setState(
            "ok" if getattr(state, "addon_found", False) else "empty",
            "INSTALLIERT" if getattr(state, "addon_found", False)
            else "FEHLT",
        )

        connected = bool(getattr(state, "discord_connected", False))

        self.rows["discord"].setState("ok" if connected else "empty")

        #
        # Das Roster hängt am Discord-Konto: ohne Verknüpfung gibt es
        # keinen Abgleich, und "aus" wäre dort die falsche Auskunft -
        # es ist nicht abgeschaltet, es fehlt die Voraussetzung.
        #

        self.rows["roster"].setState(
            "ok" if connected else "empty",
            "AKTIV" if connected else "OHNE KONTO",
        )

        self.synced.setText(
            f"LETZTER ABGLEICH {last_sync}" if last_sync
            else "NOCH KEIN ABGLEICH"
        )
