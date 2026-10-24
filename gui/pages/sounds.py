"""
Töne - eigene Warntöne für "Raus da!" im Addon.

Fünf Plätze. Jeder nimmt eine Datei des Spielers auf; die Companion
wandelt sie (mit ffmpeg) in einen kurzen Ogg-Ton und legt sie in den
Begleitordner `WeintCodex_Sounds`, wo das Addon sie findet
(`core/custom_sounds.py`, Vertrag `docs/custom-sounds-bridge.md`).

`refresh()` liest nur die kleine Ablage im Addon-Ordner - kein Netz,
nichts Blockierendes (docs/architecture/navigation.md).
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core import custom_sounds as cs
from gui.pages._page import Page
from gui.theme import tokens
from gui.theme.fonts import font
from gui.theme.icons import tinted_pixmap
from gui.theme.restyle import restyle
from gui.widgets.card import Card
from gui.widgets.chip import Chip
from gui.widgets.eyebrow import eyebrow_label
from gui.widgets.wrapped_label import enable_wrap


#
# Anhören ist eine Annehmlichkeit, keine Voraussetzung: fehlt
# QtMultimedia (oder sein Backend) im Bündel, bleibt der Knopf weg.
#

try:  # pragma: no cover - abhängig vom Bündel
    from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
except Exception:  # pragma: no cover
    QAudioOutput = QMediaPlayer = None


FILE_FILTER = (
    "Töne (" + " ".join(f"*{s}" for s in cs.ACCEPTED) + ");;Alle Dateien (*)"
)


def _text(label: QLabel, colour: str, role: str = "body") -> QLabel:

    label.setFont(font(role))

    restyle(label, f"color:{colour};background:transparent;")

    return label


class _Slot(QWidget):
    """Eine Zeile: Platznummer, Name, Herkunft, Handlungen."""

    def __init__(self, page: "SoundsPage", index: int):

        super().__init__()

        self.page = page

        self.key = f"eigen{index}"

        self.sound: cs.CustomSound | None = None

        root = QHBoxLayout(self)

        root.setContentsMargins(0, tokens.SPACE[1], 0, tokens.SPACE[1])

        root.setSpacing(tokens.SPACE[2])

        self.badge = QLabel(str(index))

        self.badge.setFixedSize(32, 32)

        self.badge.setAlignment(Qt.AlignCenter)

        self.badge.setFont(font("mono"))

        root.addWidget(self.badge)

        column = QVBoxLayout()

        column.setSpacing(2)

        self.name = QLineEdit()

        self.name.setPlaceholderText("Frei")

        self.name.setMaxLength(40)

        self.name.editingFinished.connect(self._renamed)

        self.name.setFont(font("card"))

        restyle(
            self.name,
            f"QLineEdit{{background:transparent;border:1px solid transparent;"
            f"border-radius:{tokens.RADIUS['sm']}px;padding:2px 6px;"
            f"color:{tokens.TEXT['primary']};}}"
            f"QLineEdit:hover{{border-color:{tokens.BORDER['base']};}}"
            f"QLineEdit:focus{{border-color:{tokens.BORDER['strong']};"
            f"background:{tokens.SURFACE['sunken']};}}",
        )

        self.name.setToolTip("Klicken, um den Namen zu ändern - so steht er im Spiel.")

        column.addWidget(self.name)

        self.empty = _text(QLabel("Frei"), tokens.TEXT["faint"], "card")

        self.empty.setContentsMargins(7, 0, 0, 0)

        column.addWidget(self.empty)

        self.origin = _text(QLabel(), tokens.TEXT["muted"], "small")

        self.origin.setContentsMargins(7, 0, 0, 0)

        column.addWidget(self.origin)

        root.addLayout(column, 1)

        self.play = QPushButton("Anhören")

        self.play.setObjectName("secondary")

        self.play.setCursor(Qt.PointingHandCursor)

        self.play.clicked.connect(lambda: page.preview(self.sound))

        root.addWidget(self.play)

        self.choose = QPushButton()

        self.choose.setObjectName("secondary")

        self.choose.setCursor(Qt.PointingHandCursor)

        self.choose.clicked.connect(lambda: page.pick(self.key))

        root.addWidget(self.choose)

        self.remove = QPushButton("Entfernen")

        self.remove.setObjectName("ghost")

        self.remove.setCursor(Qt.PointingHandCursor)

        self.remove.clicked.connect(lambda: page.remove(self.key))

        root.addWidget(self.remove)

    def apply(self, sound: cs.CustomSound | None, can_play: bool):

        self.sound = sound

        filled = sound is not None

        accent = tokens.TEXT["primary"] if filled else tokens.TEXT["faint"]

        restyle(
            self.badge,
            f"QLabel{{color:{accent};background:{tokens.SURFACE['raised']};"
            f"border-radius:{tokens.RADIUS['md']}px;}}",
        )

        if not self.name.hasFocus():
            self.name.setText(sound.name if filled else "")

        self.name.setVisible(filled)

        self.empty.setVisible(not filled)

        self.origin.setText(
            f"aus {sound.source}" if filled and sound.source
            else ("im Spiel als „Eigener Ton“" if filled else "Datei wählen oder hierher ziehen")
        )

        self.play.setVisible(filled and can_play)

        self.choose.setText("Ersetzen …" if filled else "Datei wählen …")

        self.remove.setVisible(filled)

    def _renamed(self):

        if self.sound is not None and self.name.text().strip() != self.sound.name:
            self.page.rename(self.key, self.name.text())


class SoundsPage(Page):

    def __init__(self, manager):

        super().__init__(manager, "RAUS DA!", "Dein Warnton, deine Wahl.")

        self.setAcceptDrops(True)

        self._player = None

        self._audio = None

        #
        # Kopf: was die Seite tut, und ob umgewandelt werden kann.
        #

        intro = Card(accent=True)

        top = QHBoxLayout()

        top.setSpacing(tokens.SPACE[3])

        icon = QLabel()

        icon.setFixedSize(56, 56)

        icon.setAlignment(Qt.AlignCenter)

        icon.setPixmap(tinted_pixmap("sound", tokens.TEXT["primary"], 28))

        restyle(
            icon,
            f"QLabel{{background:{tokens.SURFACE['raised']};"
            f"border-radius:{tokens.RADIUS['lg']}px;}}",
        )

        top.addWidget(icon, alignment=Qt.AlignTop)

        text = QVBoxLayout()

        text.setSpacing(4)

        text.addWidget(eyebrow_label("EIGENE TÖNE"))

        lead = _text(QLabel(
            "Wähle bis zu fünf eigene Töne – ein Ruf, ein Gong, ein "
            "Zitat. Die Companion kürzt sie auf "
            f"{cs.MAX_SECONDS:g} Sekunden, blendet sauber aus und legt "
            "sie dem Addon hin. Im Spiel stehen sie ganz oben in der "
            "Liste unter Komfort → Raus da! → Ton."
        ), tokens.TEXT["secondary"])

        enable_wrap(lead)

        text.addWidget(lead)

        chips = QHBoxLayout()

        chips.setSpacing(tokens.SPACE[1])

        self.ffmpeg_chip = Chip("", "neutral", dot=True)

        chips.addWidget(self.ffmpeg_chip)

        self.count_chip = Chip("", "neutral")

        chips.addWidget(self.count_chip)

        chips.addStretch(1)

        text.addLayout(chips)

        top.addLayout(text, 1)

        self.add_button = QPushButton("Ton hinzufügen …")

        self.add_button.setCursor(Qt.PointingHandCursor)

        self.add_button.clicked.connect(lambda: self.pick(None))

        top.addWidget(self.add_button, alignment=Qt.AlignTop)

        intro.addLayout(top)

        self.addWidget(intro)

        #
        # Die fünf Plätze.
        #

        slots = Card()

        slots.addWidget(eyebrow_label("PLÄTZE"))

        self.slots = [_Slot(self, i) for i in range(1, cs.SLOTS + 1)]

        for slot in self.slots:
            slots.addWidget(slot)

        self.addWidget(slots)

        #
        # Meldung der letzten Handlung - und der ehrliche Hinweis, wann
        # das Spiel einen neuen Ton kennt.
        #

        self.message = _text(QLabel(), tokens.TEXT["secondary"])

        enable_wrap(self.message)

        self.addWidget(self.message)

        note = _text(QLabel(
            "Gut zu wissen: WoW lernt neue Dateien nur beim Start "
            "kennen. Nach dem ersten Hinzufügen das Spiel einmal ganz "
            "neu starten – /reload reicht dafür nicht. Die Töne liegen "
            "im eigenen Ordner „WeintCodex_Sounds“ und überstehen jedes "
            "Addon-Update."
        ), tokens.TEXT["muted"], "small")

        enable_wrap(note)

        self.addWidget(note)

        self.body.addStretch(1)

        self.refresh()

    # --------------------------------------------------

    def _addons(self):

        return getattr(self.manager.state, "addons_path", None)

    def refresh(self):

        addons = self._addons()

        sounds = {s.key: s for s in cs.load(addons)}

        can_play = QMediaPlayer is not None

        for slot in self.slots:
            slot.apply(sounds.get(slot.key), can_play)
            slot.choose.setEnabled(bool(addons))

        ffmpeg = cs.ffmpeg_path()

        self.ffmpeg_chip.setText(
            "MP3, WAV, FLAC … WERDEN UMGEWANDELT" if ffmpeg
            else "OHNE FFMPEG: NUR .OGG"
        )

        self.ffmpeg_chip.setVariant("ok" if ffmpeg else "warn")

        self.count_chip.setText(f"{len(sounds)} VON {cs.SLOTS} BELEGT")

        self.add_button.setEnabled(bool(addons) and len(sounds) < cs.SLOTS)

        if addons and self.message.text().startswith("Ohne WoW-Ordner"):
            self.message.setText("")

        if not addons:

            self.header.setTitle("Erst den WoW-Ordner finden.")

            if not self.message.text():
                self.message.setText(
                    "Ohne WoW-Ordner weiß die Companion nicht, wohin "
                    "die Töne gehören – Einstellungen → WoW-Client."
                )

        elif not sounds:

            self.header.setTitle("Noch kein eigener Ton – leg los.")

        elif len(sounds) == 1:

            self.header.setTitle("Ein eigener Ton liegt im Spiel bereit.")

        else:

            self.header.setTitle(f"{len(sounds)} eigene Töne liegen im Spiel bereit.")

    # --------------------------------------------------
    # Handlungen
    # --------------------------------------------------

    def _say(self, text: str, kind: str = "ok"):

        colour = tokens.STATE_TEXT.get(kind, tokens.TEXT["secondary"])

        restyle(self.message, f"color:{colour};background:transparent;")

        self.message.setText(text)

    def pick(self, key: str | None):

        path, _ = QFileDialog.getOpenFileName(
            self, "Ton auswählen", str(Path.home()), FILE_FILTER,
        )

        if path:
            self.add_file(path, key)

    def add_file(self, path: str, key: str | None = None):

        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:

            sound = cs.add(self._addons(), path, key=key)

        except cs.SoundError as exc:

            self._say(str(exc), "error")

            self.manager.logger.warning(f"Eigener Ton: {exc}")

        else:

            self._say(
                f"„{sound.name}“ liegt auf Platz {sound.key[-1]}. "
                "Nach dem nächsten Spielstart unter Raus da! → Ton wählbar."
            )

            self.manager.logger.success(
                f"Eigener Ton „{sound.name}“ an das Addon übergeben."
            )

        finally:

            QApplication.restoreOverrideCursor()

        self.refresh()

    def rename(self, key: str, name: str):

        try:
            cs.rename(self._addons(), key, name)
        except (cs.SoundError, OSError) as exc:
            self._say(f"Umbenennen ging nicht: {exc}", "error")

        self.refresh()

    def remove(self, key: str):

        try:
            cs.remove(self._addons(), key)
        except (cs.SoundError, OSError) as exc:
            self._say(f"Entfernen ging nicht: {exc}", "error")
        else:
            self._say(
                f"Platz {key[-1]} ist wieder frei. Wer ihn im Spiel "
                "gewählt hatte, hört wieder den Standardton."
            )

        self.refresh()

    def preview(self, sound: cs.CustomSound | None):

        if sound is None or QMediaPlayer is None:
            return

        base = cs.folder(self._addons())

        if base is None:
            return

        if self._player is None:

            self._player = QMediaPlayer(self)

            self._audio = QAudioOutput(self)

            self._player.setAudioOutput(self._audio)

        self._player.stop()

        self._player.setSource(QUrl.fromLocalFile(str(base / sound.file)))

        self._player.play()

    # --------------------------------------------------
    # Ziehen & Ablegen
    # --------------------------------------------------

    def dragEnterEvent(self, event):

        urls = event.mimeData().urls() if event.mimeData().hasUrls() else []

        if any(Path(u.toLocalFile()).suffix.lower() in cs.ACCEPTED for u in urls):
            event.acceptProposedAction()

    def dropEvent(self, event):

        for url in event.mimeData().urls():

            path = url.toLocalFile()

            if Path(path).suffix.lower() in cs.ACCEPTED:
                self.add_file(path)
