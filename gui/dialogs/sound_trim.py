"""
Schneiden eines eigenen Tons für „Raus da!“, bevor er ans Addon geht.

Wunsch des Besitzers: „Man lädt die mp3 hoch und kann dann in der
Companion einstellen, von wann bis wann der Ton gehen soll. Mit
Speichern wird dann alles übernommen."

Der Dialog nimmt nichts selbst vor: er zeigt die Wellenform
(`custom_sounds.waveform`), lässt Start und Ende wählen - Ziehen im
Bild oder auf die Zehntelsekunde in den Feldern - und spielt zur Probe
genau den Ausschnitt, der gespeichert würde (`custom_sounds.convert` in
eine Zwischendatei). Übernommen wird erst mit „Speichern"; das Schreiben
in den Ordner des Addons macht weiter `custom_sounds.add()`.

Ein Ausschnitt ist höchstens `MAX_SECONDS` lang - ein Alarm ist ein
Signal, kein Lied. Wer weiter zieht, verschiebt den Start mit.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from PySide6.QtCore import QLocale, QRectF, Qt, QUrl, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core import custom_sounds as cs
from gui.theme import tokens
from gui.theme.fonts import font
from gui.theme.restyle import restyle
from gui.theme.theme_manager import theme
from gui.widgets.eyebrow import eyebrow_label
from gui.widgets.wrapped_label import enable_wrap

try:
    from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
except Exception:  # pragma: no cover - ohne Multimedia kein Probehören
    QAudioOutput = QMediaPlayer = None


def _de(value: float) -> str:
    """Eine Nachkommastelle mit deutschem Komma."""

    return f"{value:.1f}".replace(".", ",")


def selection(start: float, end: float, duration: float, moved: str) -> tuple[float, float]:
    """
    Start und Ende in Ordnung bringen: in der Datei, Start vor Ende,
    Abstand zwischen MIN_SECONDS und MAX_SECONDS. `moved` ("start"/"end")
    sagt, welcher Rand gerade bewegt wurde - der andere gibt nach.
    """

    start = min(max(0.0, start), duration)

    end = min(max(0.0, end), duration)

    if moved == "start":

        end = min(max(end, start + cs.MIN_SECONDS), start + cs.MAX_SECONDS, duration)

        start = min(start, max(0.0, end - cs.MIN_SECONDS))

    else:

        start = max(min(start, end - cs.MIN_SECONDS), end - cs.MAX_SECONDS, 0.0)

        end = max(end, min(duration, start + cs.MIN_SECONDS))

    return round(start, 2), round(end, 2)


class Waveform(QWidget):
    """Wellenform mit Auswahl. Farben werden in paintEvent gelesen."""

    dragged = Signal(float, float, str)

    def __init__(self, peaks: list[float], duration: float, parent=None):

        super().__init__(parent)

        self.peaks = peaks

        self.duration = duration

        self.start = 0.0

        self.end = min(duration, cs.MAX_SECONDS)

        self._anchor = None

        self.setMinimumHeight(110)

        #
        # Der Zeiger sagt, was ein Ziehen tut - schon beim Drüberfahren
        # (Wunsch nach 1.4.0): ohne Mausverfolgung meldet Qt Bewegungen nur
        # bei gedrückter Taste, der Zeiger hätte sich nie geändert.
        #

        self.setMouseTracking(True)

        self.setCursor(Qt.CrossCursor)

    def set_range(self, start: float, end: float):

        self.start, self.end = start, end

        self.update()

    def _seconds(self, x: float) -> float:

        width = max(1, self.width())

        return max(0.0, min(self.duration, x / width * self.duration))

    GRIP = 8   # so viele Bildpunkte um eine Kante greifen sie

    def zone(self, x: float) -> str:
        """Was unter dem Zeiger liegt: "start"/"end" (Kante), "inside", "outside"."""

        if self.duration <= 0:
            return "outside"

        width = max(1, self.width())

        xs = self.start / self.duration * width

        xe = self.end / self.duration * width

        if abs(x - xe) <= self.GRIP:
            return "end"

        if abs(x - xs) <= self.GRIP:
            return "start"

        if xs < x < xe:
            return "inside"

        return "outside"

    CURSORS = {
        "start": Qt.SizeHorCursor,
        "end": Qt.SizeHorCursor,
        "inside": Qt.OpenHandCursor,
        "outside": Qt.CrossCursor,
    }

    def mousePressEvent(self, event):

        if event.button() != Qt.LeftButton:
            return

        x = event.position().x()

        t = self._seconds(x)

        where = self.zone(x)

        if where == "end":
            self._anchor = ("end", self.start)
        elif where == "start":
            self._anchor = ("start", self.end)
        elif where == "inside":
            # Den ganzen Ausschnitt verschieben, die Länge bleibt.
            self._anchor = ("move", t - self.start)
            self.setCursor(Qt.ClosedHandCursor)
        else:
            self._anchor = ("new", t)
            self.dragged.emit(t, t + cs.MAX_SECONDS, "start")

    def mouseMoveEvent(self, event):

        x = event.position().x()

        if not self._anchor:
            self.setCursor(self.CURSORS[self.zone(x)])
            return

        t = self._seconds(x)

        kind, fixed = self._anchor

        if kind == "move":
            length = self.end - self.start
            start = min(max(0.0, t - fixed), max(0.0, self.duration - length))
            self.dragged.emit(start, start + length, "end")
        elif kind == "start":
            self.dragged.emit(t, fixed, "start")
        elif t >= fixed:
            self.dragged.emit(fixed, t, "end")
        else:
            self.dragged.emit(t, fixed, "start")

    def mouseReleaseEvent(self, event):

        self._anchor = None

        self.setCursor(self.CURSORS[self.zone(event.position().x())])

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing, False)

        rect = self.rect()

        painter.fillRect(rect, QColor(tokens.SURFACE["sunken"]))

        accent = QColor(theme().accent_base())

        dim = QColor(tokens.TEXT["faint"])

        if self.duration > 0:

            x0 = self.start / self.duration * rect.width()

            x1 = self.end / self.duration * rect.width()

            shade = QColor(accent)

            shade.setAlpha(45)

            painter.fillRect(QRectF(x0, 0, max(1.0, x1 - x0), rect.height()), shade)

        mid = rect.height() / 2

        count = len(self.peaks)

        if count:

            bar = rect.width() / count

            for i, peak in enumerate(self.peaks):

                x = i * bar

                t = (i + 0.5) / count * self.duration

                inside = self.start <= t <= self.end

                h = max(1.0, peak * (rect.height() / 2 - 4))

                painter.fillRect(QRectF(x, mid - h, max(1.0, bar - 1), 2 * h),
                                 accent if inside else dim)

        if self.duration > 0:

            painter.setPen(accent)

            for t in (self.start, self.end):

                x = t / self.duration * rect.width()

                painter.drawLine(int(x), 0, int(x), rect.height())

        painter.end()


class SoundTrimDialog(QDialog):
    """
    Wahl von Start und Ende. Nach `exec()` stehen `start`, `end` und
    `name` bereit; übernommen wird nur bei Accepted.
    """

    def __init__(self, source: str, ffmpeg: str, parent=None, name: str = ""):

        super().__init__(parent)

        self.source = Path(source)

        self.ffmpeg = ffmpeg

        self.duration = cs.probe_duration(self.source, ffmpeg)

        self.peaks = cs.waveform(self.source, ffmpeg) if self.duration else []

        self.start = 0.0

        self.end = min(self.duration or cs.MAX_SECONDS, cs.MAX_SECONDS)

        self.name = name or self.source.stem

        self._player = None

        self._audio = None

        self._preview = None

        self.setWindowTitle("Ton schneiden")

        self.setModal(True)

        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet(f"QDialog{{background:{tokens.SURFACE['card']};}}")

        self.setMinimumWidth(620)

        root = QVBoxLayout(self)

        root.setContentsMargins(24, 22, 24, 20)

        root.setSpacing(12)

        root.addWidget(eyebrow_label("TON SCHNEIDEN"))

        title = QLabel(self.source.name)

        title.setFont(font("title"))

        enable_wrap(title)

        restyle(title, f"color:{tokens.TEXT['primary']};background:transparent;")

        root.addWidget(title)

        self.hint = QLabel("")

        self.hint.setFont(font("small"))

        enable_wrap(self.hint)

        restyle(self.hint, f"color:{tokens.TEXT['secondary']};background:transparent;")

        root.addWidget(self.hint)

        self.wave = None

        if self.duration:

            self.wave = Waveform(self.peaks, self.duration, self)

            self.wave.dragged.connect(self._dragged)

            root.addWidget(self.wave)

        fields = QHBoxLayout()

        fields.setSpacing(10)

        self.start_box = self._spin("Start")

        self.end_box = self._spin("Ende")

        for label, box in (("Von", self.start_box), ("Bis", self.end_box)):

            text = QLabel(label)

            text.setFont(font("body"))

            restyle(text, f"color:{tokens.TEXT['secondary']};background:transparent;")

            fields.addWidget(text)

            fields.addWidget(box)

        self.length = QLabel("")

        self.length.setFont(font("body"))

        restyle(self.length, f"color:{tokens.TEXT['primary']};background:transparent;")

        fields.addWidget(self.length)

        fields.addStretch(1)

        root.addLayout(fields)

        self.message = QLabel("")

        self.message.setFont(font("small"))

        enable_wrap(self.message)

        root.addWidget(self.message)

        buttons = QHBoxLayout()

        self.play_button = QPushButton("Probe hören")

        self.play_button.setObjectName("secondary")

        self.play_button.setCursor(Qt.PointingHandCursor)

        self.play_button.clicked.connect(self.preview)

        self.play_button.setVisible(QMediaPlayer is not None and bool(self.duration))

        buttons.addWidget(self.play_button)

        buttons.addStretch(1)

        cancel = QPushButton("Abbrechen")

        cancel.setObjectName("secondary")

        cancel.setCursor(Qt.PointingHandCursor)

        cancel.clicked.connect(self.reject)

        buttons.addWidget(cancel)

        self.save_button = QPushButton("Speichern")

        self.save_button.setCursor(Qt.PointingHandCursor)

        self.save_button.setDefault(True)

        self.save_button.clicked.connect(self.accept)

        buttons.addWidget(self.save_button)

        root.addLayout(buttons)

        if self.duration:

            self.hint.setText(
                f"Die Datei ist {_de(self.duration)} s lang. Zieh im Bild, von wo bis wo "
                f"der Alarm klingen soll – höchstens {cs.MAX_SECONDS:.0f} s. Am Ende "
                "blendet er kurz aus."
            )

            self._apply(self.start, self.end, "start")

        else:

            # Länge unbekannt: kein Bild, nichts geraten - dann die ersten Sekunden.
            self.hint.setText(
                "Die Länge der Datei ließ sich nicht lesen. Gespeichert werden die "
                f"ersten {cs.MAX_SECONDS:.0f} Sekunden."
            )

            self.start_box.setEnabled(False)

            self.end_box.setEnabled(False)

            self.start, self.end = 0.0, None

    def _spin(self, name: str) -> QDoubleSpinBox:

        box = QDoubleSpinBox(self)

        box.setLocale(QLocale(QLocale.German, QLocale.Germany))

        box.setDecimals(2)

        box.setSingleStep(0.1)

        box.setSuffix(" s")

        box.setRange(0.0, self.duration or cs.MAX_SECONDS)

        box.setAccessibleName(name)

        box.valueChanged.connect(lambda _v, b=box: self._typed(b))

        return box

    def _typed(self, box):

        if getattr(self, "_updating", False):
            return

        moved = "start" if box is self.start_box else "end"

        self._apply(self.start_box.value(), self.end_box.value(), moved)

    def _dragged(self, start: float, end: float, moved: str):

        self._apply(start, end, moved)

    def _apply(self, start: float, end: float, moved: str):

        if not self.duration:
            return

        self.start, self.end = selection(start, end, self.duration, moved)

        self._updating = True

        self.start_box.setValue(self.start)

        self.end_box.setValue(self.end)

        self._updating = False

        self.length.setText(f"Länge {_de(self.end - self.start)} s")

        if self.wave is not None:
            self.wave.set_range(self.start, self.end)

    def _say(self, text: str, kind: str = "ok"):

        colour = tokens.STATE_TEXT.get(kind, tokens.TEXT["secondary"])

        restyle(self.message, f"color:{colour};background:transparent;")

        self.message.setText(text)

    def preview(self):
        """Genau den Ausschnitt hören, der gespeichert würde."""

        if QMediaPlayer is None or not self.duration:
            return

        try:

            start, length = cs.clip_window(self.start, self.end, self.duration)

            if self._preview is None:
                handle = tempfile.NamedTemporaryFile(prefix="weint_probe_", suffix=".ogg", delete=False)
                handle.close()
                self._preview = Path(handle.name)

            if self._player is not None:
                self._player.stop()
                self._player.setSource(QUrl())

            cs.convert(self.source, self._preview, self.ffmpeg, start, length)

        except cs.SoundError as exc:

            self._say(str(exc), "error")

            return

        if self._player is None:

            self._player = QMediaPlayer(self)

            self._audio = QAudioOutput(self)

            self._player.setAudioOutput(self._audio)

        self._player.setSource(QUrl.fromLocalFile(str(self._preview)))

        self._player.play()

        self._say("")

    def done(self, result):

        if self._player is not None:
            self._player.stop()
            self._player.setSource(QUrl())

        if self._preview is not None:
            try:
                self._preview.unlink()
            except OSError:
                pass
            self._preview = None

        super().done(result)
