from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.forever_switch import SEEN_KEY, needs_notice
from gui.theme.colors import Colors
from gui.theme.metrics import Metrics
from gui.widgets.hero_banner import HeroButton


class ForeverSwitchNoticeDialog(QDialog):
    """
    Einmaliger Hinweis für alle, die per Update von der alten
    Companion (Mists of Pandaria) herübergekommen sind: den Beta-Ordner
    in den Einstellungen prüfen, bevor Codex installiert wird. Warum
    das nötig ist, steht in `core/forever_switch.py`. Aufbau wie
    `DiscordLinkPromptDialog` (Text in einer QScrollArea, damit nichts
    abgeschnitten wird).
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._settings_requested = False

        self.setWindowTitle("WeintCompanion")

        self.setModal(True)

        self.setFixedSize(480, 360)

        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet(f"""
        QDialog{{
            background:{Colors.SURFACE};
            border:1px solid {Colors.BORDER_LIGHT};
            border-radius:{Metrics.RADIUS_LARGE}px;
        }}
        """)

        root = QVBoxLayout(self)

        root.setContentsMargins(32, 28, 32, 24)
        root.setSpacing(16)

        content = QWidget()

        content_layout = QVBoxLayout(content)

        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        title = QLabel("Willkommen bei WeintCompanion Forever")

        title.setWordWrap(True)

        title.setStyleSheet(
            f"font-size:18px;font-weight:700;color:{Colors.WHITE};"
        )

        content_layout.addWidget(title)

        body = QLabel(
            "Deine Companion ist auf die Fassung für World of Warcraft: "
            "Forever umgestiegen. Deine Einstellungen und deine "
            "Discord-Verknüpfung sind übernommen.\n\n"
            "Eines bitte einmal selbst prüfen: Unter Einstellungen → "
            "WoW-Client muss der Ordner deiner Forever-Beta ausgewählt "
            "sein. Erst dann installiert die Companion WeintCodex "
            "Forever an die richtige Stelle. Den Ordner deines bisherigen "
            "Spiels übernimmt sie absichtlich nicht."
        )

        body.setWordWrap(True)

        body.setStyleSheet(
            f"font-size:14px;color:{Colors.TEXT_SECONDARY};"
        )

        content_layout.addWidget(body)

        content_layout.addStretch()

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setFrameShape(QFrame.NoFrame)

        scroll.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}"
        )

        scroll.setWidget(content)

        root.addWidget(scroll, 1)

        footer = QHBoxLayout()

        footer.setSpacing(12)

        footer.addStretch()

        self.later_button = HeroButton("Später", primary=False)

        self.later_button.clicked.connect(self.reject)

        footer.addWidget(self.later_button)

        self.settings_button = HeroButton("Einstellungen öffnen", primary=True)

        self.settings_button.clicked.connect(self._request_settings)

        footer.addWidget(self.settings_button)

        root.addLayout(footer)

    # --------------------------------------------------

    @property
    def settings_requested(self) -> bool:
        return self._settings_requested

    def _request_settings(self):

        self._settings_requested = True

        self.accept()


def show_forever_switch_notice_if_needed(manager, parent=None) -> None:
    """
    Wird einmal beim Start aufgerufen (siehe gui/main_window.py), vor
    allen anderen Start-Hinweisen: wer umgestiegen ist, soll zuerst
    erfahren, warum die App anders aussieht, und wo er nachsehen muss.

    Der Vermerk wird VOR dem Anzeigen gesetzt - auch "Später" und das
    Schliessen zählen als gesehen. Der Hinweis ist eine Information,
    keine Pflicht; bei jedem Start erneut wäre er eine Gängelung.
    """

    config = manager.config

    if not needs_notice(config.data):
        return

    config.data[SEEN_KEY] = True

    config.save()

    dialog = ForeverSwitchNoticeDialog(parent)

    dialog.exec()

    if (
        dialog.settings_requested
        and parent is not None
        and hasattr(parent, "open_settings_section")
    ):

        parent.open_settings_section("wow_client")
