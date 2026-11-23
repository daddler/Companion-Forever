"""
Ein umbrechendes Label, das seine Höhe kennt.

`QLabel` mit `setWordWrap(True)` ist in senkrechten Layouts eine
verlässliche Fehlerquelle: seine `sizeHint()` beschreibt die Größe
**einer** Zeile, die tatsächliche Höhe ergibt sich aber erst aus der
Breite, die das Layout ihm zuteilt (`heightForWidth`). Ein
`QVBoxLayout` fragt das nicht immer ab - besonders dann nicht, wenn
das Element mit einer Ausrichtung hinzugefügt wurde. Das Ergebnis ist
ein Label, das mehr Zeilen zeichnet, als es für sich reklamiert hat,
und die folgenden Widgets überschreibt.

Sichtbar war das als Erklärungstext, der quer durch Titel und Knopf
eines Leerzustands lief.

Die Lösung hier ist absichtlich stumpf: die Breite steht fest, und die
Höhe wird bei jeder Textänderung mit `QFontMetrics` **ausgemessen**
statt geschätzt. Das ist der einzige Weg, der nicht davon abhängt,
wann und ob das Layout `heightForWidth` aufruft.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QRect, Qt
from PySide6.QtWidgets import QLabel, QSizePolicy


def enable_wrap(label: QLabel) -> QLabel:
    """
    Umbruch für ein Label mit **veränderlicher** Breite.

    `WrappedLabel` misst gegen eine feste Breite und ist deshalb der
    falsche Weg, sobald das Label mitwachsen soll. Hier hilft nur, Qt
    zu sagen, dass die Höhe von der Breite abhängt: `QLabel` beherrscht
    `heightForWidth()`, wenn `wordWrap` gesetzt ist, aber ein
    `QVBoxLayout` fragt es nur ab, wenn die **Größenrichtlinie** das
    ankündigt. Ohne dieses eine Flag meldet das Label die Höhe einer
    Zeile, und die folgenden Widgets werden darüber gezeichnet - genau
    die Überlagerung, die auf der Übersicht bei 960 px auftrat.
    """

    label.setWordWrap(True)

    policy = label.sizePolicy()

    policy.setHeightForWidth(True)

    label.setSizePolicy(policy)

    return label


class WrappedLabel(QLabel):

    def __init__(self, text: str = "", width: int = 420, parent=None):

        super().__init__(text, parent)

        self._wrap_width = width

        self.setWordWrap(True)

        self.setFixedWidth(width)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        self._measure()

    # --------------------------------------------------

    def setText(self, text: str):

        if text == self.text():
            return

        super().setText(text)

        self._measure()

    def setWrapWidth(self, width: int):

        if width == self._wrap_width:
            return

        self._wrap_width = width

        self.setFixedWidth(width)

        self._measure()

    def setFont(self, font):

        super().setFont(font)

        #
        # Die Schrift bestimmt die Höhe mit - nach einem Wechsel der
        # Dichte oder der Schriftrolle muss neu gemessen werden.
        #

        self._measure()

    # --------------------------------------------------

    def _measure(self):

        metrics = self.fontMetrics()

        rect = metrics.boundingRect(
            QRect(0, 0, self._wrap_width, 0),
            Qt.TextWordWrap | int(self.alignment()),
            self.text(),
        )

        self.setMinimumHeight(rect.height())


class _FitFilter(QObject):

    def eventFilter(self, obj, event):

        if event.type() in (QEvent.Resize, QEvent.FontChange, QEvent.Show):
            _fit(obj)

        return False


def _fit(label: QLabel) -> None:

    width = label.width()

    if width <= 0:
        return

    margins = label.contentsMargins()

    rect = label.fontMetrics().boundingRect(
        QRect(0, 0, max(1, width - margins.left() - margins.right()), 0),
        Qt.TextWordWrap | int(label.alignment()),
        label.text(),
    )

    height = rect.height() + margins.top() + margins.bottom() if label.text() else 0

    if label.minimumHeight() != height:
        label.setMinimumHeight(height)


def fit_wrap(label: QLabel) -> QLabel:
    """
    Wie `enable_wrap`, aber die Mindesthöhe folgt der **tatsächlichen**
    Breite: bei jeder Größen- und Textänderung ausgemessen.

    Nötig, wo das Label in einer Karte neben einer zweiten Karte steht
    (`QHBoxLayout` in einem `QStackedWidget`): dort kommt
    `heightForWidth` nicht bis nach oben durch, die Karte bekommt die
    Höhe einer Zeile, und der zweizeilige Hinweis lag über der Liste
    (Berufe-Seite, 1.0.9).
    """

    enable_wrap(label)

    fit = _FitFilter(label)

    label.installEventFilter(fit)

    label._fit_filter = fit

    original = label.setText

    def set_text(text):
        original(text)
        _fit(label)

    label.setText = set_text

    return label
