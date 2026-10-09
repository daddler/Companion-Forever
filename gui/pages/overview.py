"""
Die Übersicht - die neue Startseite.

**Warum sie das Dashboard ablöst.** Bis 1.7 zeigte die Startseite den
Zustand der Installation: WoW gefunden? Addon installiert? Updates?
Sicherungen? Das ist genau einmal interessant, nämlich am ersten Tag.
Danach ist dort alles dauerhaft grün, und der Bereich, den der Nutzer
bei jedem Start als erstes sieht, sagt ihm nichts, was er nicht schon
weiß.

Die Übersicht zeigt stattdessen, **was heute ansteht**. Bis 5.0 waren
das der nächste Raid mit Countdown und Aufstellung, der letzte Pull und
der Stand der Vorbereitung - alles Mists of Pandaria. Seit 5.1
(Forever), wo es noch keinen Raid gibt und keine Verzauberungen und
Sockel: WeintCodex selbst (Fassung, Update, was in ihr steckt), was zu
tun ist, deine Charaktere mit Stufe, und Gold und Bestand über alle
Charaktere aus dem Spielstand des Addons.

Der Installationszustand verschwindet dabei nicht, er verliert nur
seinen Rang: er sitzt als **eine einzige Zeile** am Fuß und klappt
sich nur auf, wenn tatsächlich etwas zu tun ist. Sind alle vier Punkte
in Ordnung, bleibt sie geschlossen und trägt nicht einmal einen Knopf -
das ist der ganze Unterschied zwischen "Zustand melden" und "zur
Handlung auffordern".

Was keine Daten hat, zeigt seinen Leerzustand statt erfundener
Zahlen; die Gründe stehen jeweils an Ort und Stelle.
"""

from __future__ import annotations

import threading
import time

from PySide6.QtCore import (
    QRectF,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRegion,
)
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.backend_config import app_url
from core.browser import open_url
from core.changelog_reader import format_changelog_body, strip_markdown
from core.changelog_source import (
    ADDON,
    COMPANION,
    LABELS,
    entries_for,
    find_entry,
    update_note,
)
from core.greeting import greeting, headline
from core.inventory import money_text
from core.platform import is_linux
from gui.dialogs.changelog_dialog import show_changelog
from gui.motion.pulse_clock import KIND_WARN, OPACITY_LOW, pulse_clock
from gui.controllers.inventory_loader import inventory_loader
from gui.pages._page import Page
from gui.theme import tokens
from gui.theme.fonts import font
from gui.theme.icons import tinted_pixmap
from gui.theme.motion import is_reduced
from gui.theme.restyle import restyle
from gui.theme.theme_manager import theme
from gui.theme.wow_colors import class_color
from gui.widgets.card import Card
from gui.widgets.chip import Chip
from gui.widgets.class_avatar import ClassAvatar
from gui.widgets.eyebrow import eyebrow_label
from gui.widgets.hero_banner import HeroButton
from gui.widgets.bridge_tile import BridgeTile
from gui.widgets.task_card import (
    URGENCY_BLOCKING,
    URGENCY_DUE,
    URGENCY_IDLE,
    Task,
    TaskCard,
)
from gui.widgets.wrapped_label import enable_wrap


#
# Wie viele Zeilen der Auszug im Update-Hinweis trägt. Drei sind der
# Punkt, an dem er noch überflogen wird; alles darüber gehört in die
# vollständige Ansicht, die einen Klick entfernt ist.
#

EXCERPT_LINES = 3

EXCERPT_CHARS = 260


#
# Die gemalten Masse des Update-Hinweises.
#
# Die Leiste ist absichtlich schmal: sie soll die Zeile anschieben,
# nicht sie einrahmen. Drei Pixel sind auf jedem Bildschirm noch eine
# Kante und auf keinem schon ein Balken.
#

RAIL_WIDTH = 3

ICON_TILE = 38

ICON_GLYPH = 20

#
# Deckkraft der getoenten Flaeche und ihres Rahmens. Beide liegen
# unter den Chip-Werten (TINT_SURFACE/TINT_BORDER): der Chip ist eine
# kleine Pille, diese Flaeche ist gross, und dieselbe Deckkraft waere
# ueber diese Groesse eine farbige Kachel statt einer Tonung.
#

SURFACE_ALPHA = 0.075

BORDER_ALPHA = 0.26

#
# Der atmende Ring um die Karte. `RING_ALPHA_MAX` ist der **Ruhewert** -
# er steht, wenn nicht gepulst werden darf (reduzierte Bewegung, oder
# ein sichtbares LIVE-Zeichen anderswo). Der Schein innen traegt einen
# Bruchteil davon.
#

RING_ALPHA_MIN = 0.24

RING_ALPHA_MAX = 0.62

GLOW_SHARE = 0.30

#
# Wie breit das Band an der Kante ist, das der Ring einnimmt - und
# damit das einzige, was je Bild neu gezeichnet werden muss. Es liegt
# unter der Innenpolsterung der Karte (16 px in der dichten, 20 px in
# der bequemen Einstellung), die Beschriftungen darin sind also nicht
# betroffen.
#

RING_BAND = 6


def ring_strength(opacity: float) -> float:
    """
    Die Deckkraft des Rings zu einer Phase der Pulsuhr.

    Eigene Funktion und nicht drei Zeilen im `paintEvent`, weil hier
    die eine Eigenschaft steht, die sich nicht ansehen laesst: bei
    **1.0** - also wenn gerade nicht gepulst werden darf - kommt
    `RING_ALPHA_MAX` heraus und nicht etwa der Mittelwert. Reduzierte
    Bewegung und ein sichtbares LIVE-Zeichen halten die Uhr an, und
    der Hinweis muss dann in voller Staerke stehenbleiben statt in dem
    Zwischenwert, den ein "Mittelwert bei Stillstand" ergaebe. Ein
    stehengebliebener, halb sichtbarer Ring saehe aus wie ein
    Zeichenfehler.

    Die untere Grenze kommt aus `pulse_clock`, weil sie dort gesetzt
    wird - eine zweite 0.35 hier waere eine Zahl, die stillschweigend
    auseinanderlaufen kann.
    """

    share = (opacity - OPACITY_LOW) / (1.0 - OPACITY_LOW)

    share = max(0.0, min(1.0, share))

    return RING_ALPHA_MIN + (RING_ALPHA_MAX - RING_ALPHA_MIN) * share


def ring_alpha() -> float:
    """
    Die Deckkraft, die der Ring in diesem Augenblick tragen soll.

    `is_reduced()` wird hier gefragt und nicht der Uhr überlassen: die
    Uhr entscheidet über ihren Zeitgeber nur beim An- und Abmelden, und
    wer die Einstellung umlegt, während die Karte auf dem Schirm steht,
    meldet sich dabei weder an noch ab. Der `StatusDot` fragt aus
    demselben Grund in seinem eigenen `paintEvent` - wer sich darauf
    verlässt, dass die Uhr schon stehen wird, bewegt sich bei genau der
    Einstellung weiter, die das verbietet.
    """

    if is_reduced():
        return RING_ALPHA_MAX

    return ring_strength(
        pulse_clock().opacity(KIND_WARN)
    )


def _note_head(note, installed: str) -> str:
    """
    Die Zeile über dem Auszug: **welche Fassung** er beschreibt.

    Ohne sie ist der Auszug unbeschriftet, und ein unbeschrifteter
    Text unter "Update verfügbar" wird als Inhalt des Updates gelesen.
    Was das Update mitbringt, steht hinter "Alle Änderungen ansehen" -
    hier steht, was man gerade hat.
    """

    if note is None:
        return ""

    return f"Das steckt in deiner Fassung {note.version}:"


def _excerpt(note, installed: str = "") -> str:
    """
    Die ersten Zeilen der Notizen zur **installierten** Fassung.

    Ohne Notizen ein Satz, der sagt, dass es keine gibt - und nicht
    etwa nichts. Eine leere Fläche unter "Update verfügbar" liest sich
    wie ein Ladefehler. Der Text einer Fassung, die hier noch gar
    nicht liegt, ist an dieser Stelle aber die schlechtere Antwort als
    gar keiner: er beschreibt etwas, das niemand nachsehen kann.
    """

    if note is None:

        return (
            f"Zu deiner Fassung {installed} liegen keine Notizen vor."
            if installed
            else "Zu deiner Fassung liegen keine Notizen vor."
        )

    text = format_changelog_body(note.body)

    lines = [line for line in text.splitlines() if line.strip()]

    excerpt = "\n".join(lines[:EXCERPT_LINES])

    if len(excerpt) > EXCERPT_CHARS:

        excerpt = excerpt[:EXCERPT_CHARS].rstrip() + " …"

    return excerpt or "Zu deiner Fassung liegen keine Notizen vor."


def _divider() -> QFrame:
    """
    Eine 1-px-Trennlinie innerhalb einer Karte.

    Sie ist erlaubt und widerspricht der Regel "keine Rahmen" nicht:
    ein Rahmen umschließt, eine Trennlinie gliedert.
    """

    line = QFrame()

    line.setFixedHeight(1)

    line.setStyleSheet(f"background:{tokens.SURFACE['raised']};border:none;")

    return line


class UpdateRow(QFrame):
    """
    Eine Komponente mit wartendem Update: Name, Fassung, Auszug,
    Knopf.

    **Warum die Zeile gemalt wird und keine Stylesheet-Fläche mehr
    ist.** Bis 2.3.5 war sie eine Karte in Kartenfarbe auf einer Karte
    in Kartenfarbe - dieselbe Fläche, derselbe Radius, kein Rand. Auf
    dem Bildschirm stand damit an der auffälligsten Stelle der
    Übersicht ein Block, der sich von der Aufstellung darunter nur
    durch seine Beschriftung unterschied. Ein wartendes Update ist
    aber das einzige auf dieser Seite, das eine **Handlung** verlangt;
    es muss sich vom Rest unterscheiden, bevor jemand es liest.

    Drei gemalte Mittel dafür, alle drei in Akzentfarbe und alle drei
    im `paintEvent` gelesen - eine im Konstruktor gemerkte Farbe
    überlebt den Wechsel der Akzentvariante und bleibt lautlos falsch
    (siehe CLAUDE.md):

    1. **Eine senkrechte Leiste** an der linken Kante. Sie ist das
       Zeichen, das man auch dann sieht, wenn man die Seite nur
       überfliegt.
    2. **Eine getönte Fläche** statt der Kartenfarbe, damit die Zeile
       vor der Karte liegt statt in ihr.
    3. **Ein 1-px-Rahmen**, weil eine getönte Fläche ohne Kante bei
       dieser Deckkraft als Verschmutzung des Verlaufs gelesen wird.

    Dazu die Symbolkachel: der Pfeil nach unten ist das einzige
    Element hier, das ohne Sprache sagt, worum es geht.
    """

    updateRequested = Signal(str)

    changelogRequested = Signal(str)

    def __init__(self, component: str, parent=None):

        super().__init__(parent)

        self.component = component

        self.setObjectName("updateRow")

        #
        # **Kein** WA_StyledBackground und keine Flächenregel: die
        # Zeile malt ihre Fläche selbst, und zwar mit Deckkraft. Eine
        # vom Stylesheet gefüllte Fläche läge deckend darüber, und der
        # Verlauf der Karte wäre darunter weg.
        #

        root = QHBoxLayout(self)

        root.setContentsMargins(
            RAIL_WIDTH + 13,
            12,
            14,
            12,
        )

        root.setSpacing(tokens.SPACE[2])

        #
        # Die Symbolkachel. Sie steht oben statt mittig: die Zeile
        # wächst mit dem Auszug, und ein mittig ausgerichtetes Symbol
        # wandert dann von der Überschrift weg, zu der es gehört.
        #

        self.icon = QLabel()

        self.icon.setFixedSize(ICON_TILE, ICON_TILE)

        self.icon.setAlignment(Qt.AlignCenter)

        self.icon.setAttribute(Qt.WA_StyledBackground, True)

        root.addWidget(self.icon, 0, Qt.AlignTop)

        body = QVBoxLayout()

        body.setContentsMargins(0, 0, 0, 0)

        body.setSpacing(6)

        root.addLayout(body, 1)

        head = QHBoxLayout()

        head.setContentsMargins(0, 0, 0, 0)

        head.setSpacing(tokens.SPACE[1])

        self.title = QLabel("")

        self.title.setFont(font("card"))

        restyle(
            self.title,
            f"color:{tokens.WHITE};background:transparent;",
        )

        head.addWidget(self.title)

        self.versions = QLabel("")

        self.versions.setFont(font("mono"))

        restyle(
            self.versions,
            f"color:{tokens.TEXT['faint']};background:transparent;",
        )

        head.addWidget(self.versions)

        head.addStretch(1)

        body.addLayout(head)

        #
        # Der Auszug ist der eigentliche Grund für diesen Hinweis: ein
        # "Update verfügbar" ohne Inhalt beantwortet die einzige Frage
        # nicht, die man davor hat. Er beschreibt seit 2.4.1 die
        # Fassung, die **installiert** ist - und die Zeile darüber sagt
        # welche. Vorher stand hier der Text der angebotenen Fassung,
        # also einer, die auf diesem Rechner noch gar nicht liegt: ein
        # vorausschauender Absatz an einer Stelle, an der jeder eine
        # Beschreibung dessen erwartet, was er hat. Was das Update
        # bringt, steht einen Knopf weiter unter "Alle Änderungen
        # ansehen" - dort ist es auch als solches beschriftet.
        #

        self.note_head = QLabel("")

        self.note_head.setFont(font("small"))

        enable_wrap(self.note_head)

        restyle(
            self.note_head,
            f"color:{tokens.TEXT['muted']};background:transparent;",
        )

        body.addWidget(self.note_head)

        self.excerpt = QLabel("")

        self.excerpt.setFont(font("small"))

        enable_wrap(self.excerpt)

        restyle(
            self.excerpt,
            f"color:{tokens.TEXT['secondary']};background:transparent;",
        )

        body.addWidget(self.excerpt)

        actions = QHBoxLayout()

        actions.setContentsMargins(0, 0, 0, 0)

        actions.setSpacing(tokens.SPACE[1])

        #
        # Der Hauptknopf der Anwendung statt des sekundären: eine
        # Umrissfläche neben "WoW starten" in Vollfläche liest sich als
        # die weniger wichtige der beiden Handlungen - und genau
        # umgekehrt ist es hier gemeint. `HeroButton` nimmt seine
        # Farben zur Laufzeit aus dem Theme, folgt also dem Akzent.
        #

        self.install = HeroButton("Jetzt aktualisieren")

        self.install.clicked.connect(self._request_update)

        actions.addWidget(self.install)

        self.changelog = QPushButton("Alle Änderungen ansehen")

        self.changelog.setObjectName("ghost")

        self.changelog.setCursor(Qt.PointingHandCursor)

        self.changelog.clicked.connect(self._request_changelog)

        actions.addWidget(self.changelog)

        actions.addStretch(1)

        body.addLayout(actions)

        self._apply_accent()

        #
        # Gebundene Methode, keine Lambda: `theme()` ist ein Singleton
        # und lebt so lange wie der Prozess - eine Closure darin hielte
        # diese Zeile für immer am Leben (siehe CLAUDE.md und
        # tests/test_theme_connections.py).
        #

        theme().accent_changed.connect(self._on_accent)

    # --------------------------------------------------

    def _on_accent(self, _name: str = ""):

        self._apply_accent()

        self.update()

    def _apply_accent(self):
        """
        Symbol und Kachel neu einfärben.

        Das Symbol ist eine Pixmap und damit das eine Element hier, das
        einen Akzentwechsel nicht durch bloßes Neuzeichnen mitmacht -
        es muss neu eingefärbt werden.
        """

        self.icon.setPixmap(
            tinted_pixmap(
                "download",
                theme().accent_light(),
                ICON_GLYPH,
            )
        )

        restyle(
            self.icon,
            f"""
            QLabel{{
                background:{tokens.tint(
                    theme().accent_base(), 0.14
                )};
                border-radius:{tokens.RADIUS["sm"]}px;
            }}
            """,
        )

    # --------------------------------------------------

    def _request_update(self):

        self.updateRequested.emit(self.component)

    def _request_changelog(self):

        self.changelogRequested.emit(self.component)

    # --------------------------------------------------

    def apply(
        self,
        name: str,
        installed: str,
        available: str,
        excerpt: str,
        note_head: str = "",
    ):

        self.title.setText(f"{name} {available}")

        self.versions.setText(
            f"{installed} → {available}" if installed else available
        )

        self.note_head.setText(note_head)

        self.note_head.setVisible(bool(note_head))

        self.excerpt.setText(excerpt)

    def set_running(self, running: bool, note: str = ""):

        self.install.setEnabled(not running)

        self.changelog.setEnabled(not running)

        #
        # Während des Vorgangs steht der Fortschritt an der Stelle des
        # Auszugs - die Überschrift dazu wäre dann falsch, denn sie
        # nennt eine Fassung, die der Fortschrittstext nicht meint.
        #

        if running:
            self.note_head.setVisible(False)

        if note:
            self.excerpt.setText(note)

    # --------------------------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)

        radius = float(tokens.RADIUS["md"])

        base = QColor(theme().accent_base())

        shape = QPainterPath()

        shape.addRoundedRect(rect, radius, radius)

        #
        # Fläche
        #

        surface = QColor(base)

        surface.setAlphaF(SURFACE_ALPHA)

        painter.setPen(Qt.NoPen)

        painter.setBrush(surface)

        painter.drawPath(shape)

        #
        # Die Leiste. Sie wird gegen die Kartenform beschnitten statt
        # als eigenes Rechteck gezeichnet - sonst stünde sie an den
        # beiden linken Ecken über die Rundung hinaus.
        #

        painter.save()

        painter.setClipPath(shape)

        rail = QLinearGradient(
            rect.left(),
            rect.top(),
            rect.left(),
            rect.bottom(),
        )

        rail.setColorAt(0.0, QColor(theme().accent_light()))
        rail.setColorAt(1.0, base)

        painter.fillRect(
            QRectF(
                rect.left(),
                rect.top(),
                float(RAIL_WIDTH),
                rect.height(),
            ),
            rail,
        )

        painter.restore()

        #
        # Rahmen
        #

        border = QColor(base)

        border.setAlphaF(BORDER_ALPHA)

        painter.setBrush(Qt.NoBrush)

        painter.setPen(QPen(border, 1))

        painter.drawPath(shape)


class UpdateCard(Card):
    """
    Der Update-Hinweis auf der Übersicht.

    **Warum er hierher gehört.** Ein wartendes Update war an drei
    Stellen zu sehen (Systemzeile am Fuß, Abzeichen in der Navigation,
    ein Meldungsstreifen beim Start), aber an keiner davon *auslösbar*.
    Jeder Weg endete auf "Addon & Updates", also drei Klicks für eine
    Handlung, die aus einem bestehen kann. Diese Karte ist der eine
    Ort, an dem beides zusammenkommt: was kommt, und der Knopf dafür.

    Sie ersetzt die Seite "Addon & Updates" nicht - wer erst lesen
    will, was eine Fassung bringt, kommt über "Alle Änderungen
    ansehen" an den vollständigen Changelog, und die Seite bleibt für
    Sicherungen, Neuinstallation und Protokoll zuständig.

    **Sie erscheint nur, wenn wirklich etwas ansteht.** Eine dauerhaft
    sichtbare Karte "alles aktuell" wäre genau der Fehler, den die
    Übersicht 2.0 beim Dashboard behoben hat: der Bereich, den man bei
    jedem Start zuerst sieht, sagt sonst etwas, das man schon weiß.

    **Und sie atmet.** Die Karte trägt einen Ring in Akzentfarbe,
    dessen Deckkraft an der Pulsuhr hängt - derselben, an der der
    Warnpunkt am Navigationseintrag "Addon & Updates" hängt. Beide
    lesen dieselbe Phase und schwingen deshalb im Gleichtakt; zwei
    eigene Zeitgeber liefen gegeneinander und sähen nach einem Fehler
    aus (siehe `gui/motion/pulse_clock.py`). Drei Eigenschaften der Uhr
    sind hier der Grund, sie überhaupt zu benutzen statt selbst zu
    animieren:

    - **Vorrang.** Ist irgendwo ein LIVE-Zeichen sichtbar - WeintTV
      während eines laufenden Pulls -, steht der Ring still. Ein
      Update kann warten, ein laufender Kampf nicht.
    - **Reduzierte Bewegung.** Dann steht der Ring in **voller**
      Stärke (`ring_alpha()`). Der Hinweis verschwindet also nicht, er
      hört nur auf sich zu bewegen - das ist der Unterschied zwischen
      einer abgeschalteten Animation und einer abgeschalteten Aussage.
    - **Kosten.** Die Uhr läuft ohnehin, solange ein Update wartet
      (der Navigationspunkt ist immer sichtbar); dieser Ring bestellt
      keinen zweiten Zeitgeber, er liest nur mit.

    Angemeldet wird bei der **Sichtbarkeit**, nicht beim Bauen: die
    Karte wird auf jeder Übersicht gebaut, aber nur gezeigt, wenn
    etwas aussteht - eine Anmeldung im Konstruktor hielte die Uhr
    dauerhaft am Laufen, obwohl niemand pulst.
    """

    updateRequested = Signal(str)

    changelogRequested = Signal(str)

    def __init__(self, parent=None):

        super().__init__(accent=True, parent=parent)

        self._pulsing = False

        header = QHBoxLayout()

        header.setContentsMargins(0, 0, 0, 0)

        header.setSpacing(tokens.SPACE[1])

        self.eyebrow = eyebrow_label(
            "UPDATE VERFÜGBAR",
            theme().accent_light(),
        )

        header.addWidget(self.eyebrow)

        header.addStretch(1)

        #
        # Mit Punkt: er trägt dieselbe Phase wie der Ring und wie das
        # Abzeichen in der Navigationsspalte. Der Chip allein war eine
        # ruhende Angabe unter mehreren ruhenden Angaben.
        #

        self.chip = Chip("1 UPDATE", "warn", dot=True)

        header.addWidget(self.chip)

        self.addLayout(header)

        self.rows: dict[str, UpdateRow] = {}

        for component in (ADDON, COMPANION):

            row = UpdateRow(component)

            row.updateRequested.connect(self.updateRequested.emit)

            row.changelogRequested.connect(self.changelogRequested.emit)

            row.setVisible(False)

            self.rows[component] = row

            self.addWidget(row)

        #
        # Der Akzent färbt die Rubrik ein - gelesen wird er beim
        # Umschalten neu, über eine gebundene Methode statt einer
        # Closure (siehe die Notiz zu den drei Themensignalen in
        # CLAUDE.md).
        #

        theme().accent_changed.connect(self._on_accent)

    # --------------------------------------------------

    def _on_accent(self, _name: str = ""):

        self.eyebrow.setStyleSheet(
            f"color:{theme().accent_light()};background:transparent;"
        )

    def setCount(self, count: int):

        self.chip.setText(
            f"{count} UPDATES" if count != 1 else "1 UPDATE"
        )

        #
        # Auch die Rubrik: "UPDATE VERFÜGBAR" über zwei Zeilen liest
        # sich wie ein Fehler in der Karte.
        #

        self.eyebrow.setText(
            "UPDATES VERFÜGBAR" if count != 1 else "UPDATE VERFÜGBAR"
        )

    # --------------------------------------------------
    # Puls
    # --------------------------------------------------

    def showEvent(self, event):

        super().showEvent(event)

        self._claim()

    def hideEvent(self, event):

        super().hideEvent(event)

        self._release()

    def _claim(self):

        if self._pulsing:
            return

        clock = pulse_clock()

        clock.subscribe(KIND_WARN)

        clock.tick.connect(self._on_tick)

        self._pulsing = True

    def _release(self):

        if not self._pulsing:
            return

        clock = pulse_clock()

        clock.unsubscribe(KIND_WARN)

        try:
            clock.tick.disconnect(self._on_tick)

        except (RuntimeError, TypeError):
            #
            # Bereits getrennt - beim Abbau der Seite kann Qt die
            # Verbindung vor uns gelöst haben.
            #
            pass

        self._pulsing = False

    def _on_tick(self):
        """
        Nur das Band an der Kante neu anfordern, nicht die Karte.

        Ein `update()` ohne Bereich zeichnete sechzig Mal je Sekunde
        die **ganze** Karte neu - beide Zeilen mit Symbolkachel,
        Überschrift, Auszug und zwei Knöpfen, dazu Kopfzeile und Chip.
        Genau die Art Kosten je Bild, die CLAUDE.md für die
        Wiedergabe beschreibt, nur dass hier niemand darum gebeten
        hat: der Ring bewegt sich, der Inhalt steht.
        """

        rect = self.rect()

        inner = rect.adjusted(
            RING_BAND,
            RING_BAND,
            -RING_BAND,
            -RING_BAND,
        )

        self.update(
            QRegion(rect).subtracted(QRegion(inner))
        )

    # --------------------------------------------------

    def paintEvent(self, event):

        super().paintEvent(event)

        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing, True)

        radius = float(self._radius)

        base = QColor(theme().accent_base())

        strength = ring_alpha()

        painter.setBrush(Qt.NoBrush)

        #
        # Zwei Ringe: ein breiter, sehr schwacher innen als Schein und
        # ein schmaler auf der Kante. Qt kennt keinen Schlagschatten
        # ohne eigenen Grafikeffekt je Widget - und ein Effekt auf der
        # Karte legte ihren ganzen Inhalt in eine eigene Pixmap.
        #

        glow = QColor(base)

        glow.setAlphaF(strength * GLOW_SHARE)

        pen = QPen(glow, 4)

        pen.setJoinStyle(Qt.RoundJoin)

        painter.setPen(pen)

        painter.drawRoundedRect(
            QRectF(self.rect()).adjusted(2.5, 2.5, -2.5, -2.5),
            radius - 2.0,
            radius - 2.0,
        )

        ring = QColor(base)

        ring.setAlphaF(strength)

        painter.setPen(QPen(ring, 1.4))

        painter.drawRoundedRect(
            QRectF(self.rect()).adjusted(0.7, 0.7, -0.7, -0.7),
            radius,
            radius,
        )


#
# Wie viele frühere Fassungen die Codex-Karte nennt. Vier passen neben
# die rechte Spalte, ohne dass die Karte höher wird als sie.
#

HISTORY_ROWS = 4

HISTORY_CHARS = 240


def _first_line(body: str) -> str:
    """
    Die erste Aussage eines Changelog-Eintrags, ohne Überschrift und
    Aufzählungszeichen, gekürzt auf eine Zeile.
    """

    for line in (body or "").splitlines():

        line = line.strip()

        if not line or line.startswith("#"):
            continue

        line = strip_markdown(line.lstrip("-*• ").strip())

        if len(line) > HISTORY_CHARS:
            line = line[:HISTORY_CHARS].rstrip() + " …"

        return line

    return ""


class _ElidedLabel(QLabel):
    """
    Eine Zeile, die sich kürzt statt die Karte zu verbreitern.

    Die Zusammenfassung einer Fassung ist oft ein halber Absatz; als
    umbrechendes Label drückte sie die Karte in die Höhe, als
    gewöhnliches in die Breite. Gekürzt wird beim Zeichnen gegen die
    tatsächliche Breite, der volle Satz steht im Tooltip.
    """

    def __init__(self, parent=None):

        super().__init__(parent)

        self._full = ""

        policy = self.sizePolicy()

        policy.setHorizontalPolicy(policy.Policy.Ignored)

        self.setSizePolicy(policy)

    def setFullText(self, text: str):

        self._full = text

        self.setToolTip(text)

        self._elide()

    def resizeEvent(self, event):

        super().resizeEvent(event)

        self._elide()

    def _elide(self):

        self.setText(
            self.fontMetrics().elidedText(self._full, Qt.ElideRight, max(0, self.width()))
        )


class CodexCard(Card):
    """
    WeintCodex selbst - die Hauptkarte der Übersicht seit 5.1.

    An dieser Stelle stand bis 5.0 die Aufstellung des nächsten Raids
    (Termin, Countdown, Zusagen). Auf Forever gibt es noch keinen Raid,
    und eine Karte, die dauerhaft "kein Termin bekannt" sagt, ist die
    Startseite von 1.7 noch einmal: ein Platz, an dem immer dasselbe
    steht.

    Was stattdessen jeden Tag stimmt: **welche Fassung von WeintCodex
    du spielst, ob sie aktuell ist und was in ihr steckt.** Das Addon
    erscheint auf Forever im Wochentakt, und die Notizen sind der eine
    Ort, an dem man erfährt, was sich im Spiel geändert hat - ohne
    erst einzuloggen. Der Knopf zum Spiel bleibt, wo er war.
    """

    def __init__(self, parent=None):

        super().__init__(accent=True, parent=parent)

        self.setMinimumHeight(170)

        header = QHBoxLayout()

        header.setContentsMargins(0, 0, 0, 0)

        header.setSpacing(tokens.SPACE[1])

        header.addWidget(eyebrow_label("WEINTCODEX · FOREVER"))

        header.addStretch(1)

        self.chip = Chip("UNBEKANNT", "neutral")

        header.addWidget(self.chip)

        self.addLayout(header)

        self.addWidget(_divider())

        body = QHBoxLayout()

        body.setContentsMargins(0, 0, 0, 0)

        body.setSpacing(tokens.SPACE[4])

        text = QVBoxLayout()

        text.setContentsMargins(0, 0, 0, 0)

        text.setSpacing(4)

        self.title = QLabel("")

        self.title.setFont(font("section"))

        enable_wrap(self.title)

        restyle(self.title, f"color:{tokens.WHITE};background:transparent;")

        text.addWidget(self.title)

        self.head = QLabel("")

        self.head.setFont(font("small"))

        enable_wrap(self.head)

        restyle(self.head, f"color:{tokens.TEXT['muted']};background:transparent;")

        text.addSpacing(tokens.SPACE[1])

        text.addWidget(self.head)

        self.notes = QLabel("")

        self.notes.setFont(font("small"))

        enable_wrap(self.notes)

        restyle(self.notes, f"color:{tokens.TEXT['secondary']};background:transparent;")

        text.addWidget(self.notes)

        #
        # Die Fassungen davor. WeintCodex erscheint auf Forever
        # mehrmals die Woche; wer ein paar Tage nicht hingesehen hat,
        # will wissen, was seitdem kam - eine Zeile je Fassung, die
        # vollständigen Notizen hinter "Alle Änderungen".
        #

        text.addSpacing(tokens.SPACE[2])

        self.history_head = eyebrow_label("DAVOR")

        text.addWidget(self.history_head)

        self._history = []

        for _ in range(HISTORY_ROWS):

            row = QWidget()

            line = QHBoxLayout(row)

            line.setContentsMargins(0, 0, 0, 0)

            line.setSpacing(tokens.SPACE[2])

            version = QLabel("")

            version.setFont(font("mono"))

            version.setFixedWidth(84)

            restyle(version, f"color:{tokens.TEXT['primary']};background:transparent;")

            line.addWidget(version)

            summary = _ElidedLabel()

            summary.setFont(font("small"))

            restyle(summary, f"color:{tokens.TEXT['secondary']};background:transparent;")

            line.addWidget(summary, 1)

            text.addWidget(row)

            self._history.append((row, version, summary))

        text.addStretch(1)

        body.addLayout(text, 1)

        buttons = QVBoxLayout()

        buttons.setContentsMargins(0, 0, 0, 0)

        buttons.setSpacing(tokens.SPACE[1])

        self.launch = QPushButton("WoW starten")

        self.launch.setCursor(Qt.PointingHandCursor)

        buttons.addWidget(self.launch)

        self.changelog = QPushButton("Alle Änderungen")

        self.changelog.setObjectName("secondary")

        self.changelog.setCursor(Qt.PointingHandCursor)

        buttons.addWidget(self.changelog)

        self.action = QPushButton("Installieren")

        self.action.setObjectName("secondary")

        self.action.setCursor(Qt.PointingHandCursor)

        self.action.setVisible(False)

        buttons.addWidget(self.action)

        buttons.addStretch(1)

        body.addLayout(buttons)

        self.addLayout(body, 1)

    def apply(self, state, note, entries=()):
        """
        `note` ist `update_note(ADDON, state)` - die Notizen der
        **installierten** Fassung, oder `None`. `entries` sind die
        Fassungen **vor** ihr, die neueste zuerst.
        """

        self._apply_history(entries if state.addon_found else ())

        self.head.setVisible(True)

        self.notes.setVisible(True)

        if not state.wow_found:

            self.title.setText("World of Warcraft: Forever wurde noch nicht gefunden.")

            self.chip.setText("KEIN SPIEL")

            self.chip.setVariant("neutral")

            self.head.setText("")

            self.notes.setText(
                "Lege den Spielordner unter Einstellungen → WoW-Client "
                "fest. Danach installiert die App WeintCodex dorthin."
            )

            self.changelog.setVisible(False)

            self.action.setText("Spielordner festlegen")

            self.action.setVisible(True)

            return

        if not state.addon_found:

            self.title.setText("WeintCodex ist noch nicht installiert.")

            self.chip.setText("NICHT INSTALLIERT")

            self.chip.setVariant("warn")

            self.head.setText("")

            self.notes.setText(
                "Ein Klick lädt die aktuelle Fassung von GitHub und legt "
                "sie in den AddOns-Ordner - deine Einstellungen im Spiel "
                "bleiben dabei unberührt."
            )

            self.changelog.setVisible(True)

            self.action.setText("Jetzt installieren")

            self.action.setVisible(True)

            return

        version = state.addon_version or "?"

        if state.update_available:

            self.title.setText(
                f"Fassung {version} installiert - {state.github_version} ist da."
            )

            self.chip.setText("UPDATE")

            self.chip.setVariant("warn")

        else:

            self.title.setText(f"Fassung {version} installiert.")

            known = bool(state.github_version)

            self.chip.setText("AKTUELL" if known else "NICHT GEPRÜFT")

            self.chip.setVariant("ok" if known else "neutral")

        #
        # Wartet ein Update, steht derselbe Auszug schon in der
        # Update-Karte daneben - zweimal derselbe Text nebeneinander
        # liest sich wie ein Fehler. Dann bleibt hier nur der Verlauf.
        #

        pending = bool(state.update_available)

        self.head.setVisible(not pending)

        self.notes.setVisible(not pending)

        self.head.setText(_note_head(note, version))

        self.notes.setText(_excerpt(note, version))

        self.changelog.setVisible(True)

        self.action.setVisible(False)

    def _apply_history(self, entries):

        entries = list(entries)[:HISTORY_ROWS]

        self.history_head.setVisible(bool(entries))

        for index, (row, version, summary) in enumerate(self._history):

            if index >= len(entries):

                row.setVisible(False)

                continue

            entry = entries[index]

            row.setVisible(True)

            version.setText(entry.version)

            summary.setFullText(_first_line(entry.body) or "ohne Notizen")


def addon_history(state) -> list:
    """
    Die Fassungen vor der installierten, die neueste zuerst.

    Leer, wenn die installierte im Changelog nicht vorkommt - eine
    Liste "davor" ohne den Punkt, vor dem sie steht, wäre eine Liste
    von irgendwas.
    """

    entries = entries_for(ADDON, state)

    installed = find_entry(entries, getattr(state, "addon_version", "") or "")

    if installed is None:
        return []

    index = entries.index(installed)

    return entries[index + 1:index + 1 + HISTORY_ROWS]


class CharactersTile(Card):
    """
    Deine Charaktere auf einen Blick - Stufe und Gegenstandsstufe.

    Forever beginnt mit Leveln: die Frage beim Öffnen ist nicht mehr
    "bin ich für den Raid vorbereitet", sondern "wo steht wer". Die
    zuletzt gespielten zuerst; die volle Liste steht unter "Meine
    Charaktere". Daten aus `CharacterStore` - gelesen, nicht abgerufen.
    """

    ROWS = 4

    def __init__(self, parent=None):

        super().__init__(parent=parent)

        self.addWidget(eyebrow_label("DEINE CHARAKTERE"))

        self.rows = QVBoxLayout()

        self.rows.setContentsMargins(0, 0, 0, 0)

        self.rows.setSpacing(8)

        self._rows = []

        for _ in range(self.ROWS):

            row = QWidget()

            line = QHBoxLayout(row)

            line.setContentsMargins(0, 0, 0, 0)

            line.setSpacing(tokens.SPACE[1])

            avatar = ClassAvatar("", 26)

            line.addWidget(avatar)

            name = QLabel("")

            name.setFont(font("ui"))

            line.addWidget(name, 1)

            value = QLabel("")

            value.setFont(font("mono"))

            restyle(value, f"color:{tokens.TEXT['secondary']};background:transparent;")

            line.addWidget(value)

            self.rows.addWidget(row)

            self._rows.append((row, avatar, name, value))

        self.addLayout(self.rows)

        self.note = QLabel("")

        self.note.setFont(font("small"))

        enable_wrap(self.note)

        restyle(self.note, f"color:{tokens.TEXT['secondary']};background:transparent;")

        self.addWidget(self.note)

        self.addStretch(1)

        self.button = QPushButton("Alle Charaktere")

        self.button.setObjectName("secondary")

        self.button.setCursor(Qt.PointingHandCursor)

        self.addWidget(self.button)

    def apply(self, characters: list):

        characters = sorted(
            characters,
            key=lambda sheet: -(sheet.get("updated") or 0),
        )

        for index, (row, avatar, name, value) in enumerate(self._rows):

            if index >= len(characters):

                row.setVisible(False)

                continue

            sheet = characters[index]

            row.setVisible(True)

            avatar.setClass(sheet.get("class", ""))

            name.setText(sheet.get("name", "?"))

            restyle(
                name,
                f"color:{class_color(sheet.get('class', ''))};background:transparent;",
            )

            level = sheet.get("level") or 0

            item_level = sheet.get("item_level_equipped") or 0.0

            parts = [f"Stufe {level}" if level else "Stufe ?"]

            if item_level > 0:
                parts.append(f"GS {item_level:.0f}")

            value.setText(" · ".join(parts))

        if not characters:

            self.note.setText(
                "Noch kein Charakter gemeldet. WeintCodex meldet ihn beim "
                "Anmelden im Spiel."
            )

        elif len(characters) > self.ROWS:

            self.note.setText(f"und {len(characters) - self.ROWS} weitere")

        else:

            self.note.setText("")


class GoldTile(Card):
    """
    Gold und Bestand über alle Charaktere - aus dem Spielstand.

    Die Zahl kommt aus `core/inventory.py`; Charaktere ohne Goldstand
    zählen nicht mit und werden genannt, nicht verschwiegen.
    """

    def __init__(self, parent=None):

        super().__init__(parent=parent)

        self.addWidget(eyebrow_label("GOLD & BESTAND"))

        self.value = QLabel("–")

        self.value.setFont(font("displayCard"))

        restyle(self.value, f"color:{tokens.WHITE};background:transparent;")

        self.addWidget(self.value)

        self.note = QLabel("")

        self.note.setFont(font("small"))

        enable_wrap(self.note)

        restyle(self.note, f"color:{tokens.TEXT['secondary']};background:transparent;")

        self.addWidget(self.note)

        self.addStretch(1)

        self.button = QPushButton("Bestand durchsuchen")

        self.button.setObjectName("secondary")

        self.button.setCursor(Qt.PointingHandCursor)

        self.addWidget(self.button)

    def apply(self, inventory):

        if not inventory.known or not inventory.characters:

            self.value.setText("unbekannt")

            self.note.setText(
                "WeintCodex merkt sich Taschen, Bank und Gold jedes "
                "Charakters - sichtbar hier, sobald du dich einmal im "
                "Spiel an- und abgemeldet hast."
            )

            return

        total, unknown = inventory.gold()

        counted = len(inventory.characters) - unknown

        self.value.setText(money_text(total) if counted else "unbekannt")

        parts = [
            f"{len(inventory.item_ids())} verschiedene Gegenstände",
            "ein Charakter" if len(inventory.characters) == 1
            else f"{len(inventory.characters)} Charaktere",
        ]

        if unknown:
            parts.append(f"{unknown} ohne Goldstand")

        self.note.setText(" · ".join(parts) + ". Stand des letzten Ausloggens.")

class OverviewPage(Page):

    #
    # Das Ende der Update-Prüfung kommt aus einem Hintergrund-Thread
    # zurück in den Hauptthread - der Knopf ist ein Widget und darf
    # von dort nicht angefasst werden (dieselbe Regel wie bei
    # `CompanionManager.state_changed`).
    #

    checkFinished = Signal()

    def __init__(self, manager, parent=None):

        super().__init__(
            manager,
            greeting(),
            "Willkommen zurück.",
            parent,
        )

        #
        # "Erneut prüfen" - derselbe Knopf wie unter "Addon &
        # Updates". Er steht hier, weil die Übersicht die Seite ist,
        # auf der ein wartendes Update angekündigt wird (Karte,
        # Systemzeile, Abzeichen): wer dort nachsehen will, ob
        # inzwischen etwas dazugekommen ist, musste dafür bisher die
        # Seite wechseln.
        #

        self.check_button = QPushButton("Erneut prüfen")

        self.check_button.setObjectName("secondary")

        self.check_button.setCursor(Qt.PointingHandCursor)

        self.check_button.clicked.connect(self.check_updates)

        self.header.addAction(self.check_button)

        self._check_thread = None

        self.checkFinished.connect(self._on_check_finished)

        #
        # Der Minutentakt trägt die Begrüßung: "Guten Tag" wird um
        # 18 Uhr zu "Guten Abend", und die Zeitangaben am Fuss der
        # Aufgabenkarte ("vor 5 min") ziehen nach.
        #
        # Der Zeitgeber läuft nur, solange die Seite sichtbar ist -
        # `on_enter`/`on_leave` schalten ihn, wie WeintTV und die
        # Academy es mit dem Datenstrom halten.
        #

        self._clock = QTimer(self)

        self._clock.setInterval(60_000)

        self._clock.timeout.connect(self._tick)

        #
        # Der Update-Hinweis steht **über** der Aufstellung, weil er
        # eine Handlung trägt und alles darunter eine Auskunft ist.
        # Sichtbar wird er nur, wenn wirklich etwas aussteht.
        #

        self.updates = UpdateCard()

        self.updates.setVisible(False)

        self.updates.updateRequested.connect(self._start_update)

        self.updates.changelogRequested.connect(self._open_changelog)

        self._runner = None

        #
        # ==================================================
        # Hauptzeile: WeintCodex und was zu tun ist
        # ==================================================
        #
        # Die beiden zusammen beantworten die Frage, mit der jemand
        # diese Seite öffnet: *ist mein Addon in Ordnung, und muss ich
        # vorher noch was machen*. Alles darunter ist Auskunft.
        #
        # Als Raster statt als Reihe: unter 980 px stellt der
        # Haltepunkt die Karten untereinander, und ein QGridLayout
        # kann eine Karte umsetzen, ohne dass sie neu gebaut werden
        # müsste.
        #

        self.row = QGridLayout()

        self.row.setContentsMargins(0, 0, 0, 0)

        self.row.setHorizontalSpacing(20)

        self.row.setVerticalSpacing(20)

        #
        # Seit 5.1 (Forever) steht hier WeintCodex selbst und nicht mehr
        # die Aufstellung des nächsten Raids - siehe `CodexCard`.
        #

        self.codex = CodexCard()

        self.codex.launch.clicked.connect(self._launch_wow)

        self.codex.changelog.clicked.connect(self._open_addon_changelog)

        self.codex.action.clicked.connect(self._codex_action)

        self.row.addWidget(self.codex, 0, 0)

        #
        # Die rechte Spalte hat zwei Bewohner, und das ist Absicht:
        #
        # * `TaskCard` sagt, **was** zu tun ist - eine Liste mit
        #   Knöpfen, die Aufgabe wird woanders erledigt.
        # * `UpdateCard` ist das eine, was hier **selbst** passiert:
        #   sie trägt Fortschrittsbalken und Fehlermeldung eines
        #   laufenden Updates.
        #
        # Beides in eine Karte zu legen hiesse, eine Liste zu bauen,
        # in der eine Zeile plötzlich einen Balken bekommt und die
        # anderen nicht. Sie stehen deshalb untereinander, und die
        # Update-Karte ist nur da, solange sie etwas zu zeigen hat.
        #

        self.side = QVBoxLayout()

        self.side.setContentsMargins(0, 0, 0, 0)

        self.side.setSpacing(20)

        self.side.addWidget(self.updates)

        self.tasks = TaskCard()

        self.side.addWidget(self.tasks, 1)

        self.row.addLayout(self.side, 0, 1)

        self.row.setColumnStretch(0, 3)

        self.row.setColumnStretch(1, 2)

        self.row.setColumnMinimumWidth(1, 386)

        self._single_column = False

        self.addLayout(self.row, 1)

        #
        # ==================================================
        # Kachelzeile: der Rückblick
        # ==================================================
        #

        self.tiles = QGridLayout()

        self.tiles.setContentsMargins(0, 0, 0, 0)

        self.tiles.setHorizontalSpacing(20)

        self.tiles.setVerticalSpacing(20)

        self.characters = CharactersTile()

        self.characters.button.clicked.connect(self._open_characters)

        self.tiles.addWidget(self.characters, 0, 0)

        self.gold = GoldTile()

        self.gold.button.clicked.connect(self._open_inventory)

        self.tiles.addWidget(self.gold, 0, 1)

        self.loader = inventory_loader(manager)

        self.loader.changed.connect(self._on_inventory)

        self.bridges = BridgeTile()

        self.tiles.addWidget(self.bridges, 0, 2)

        for column in (0, 1, 2):
            self.tiles.setColumnStretch(column, 1)

        self.addLayout(self.tiles)

    # --------------------------------------------------

    def _launch_wow(self):
        """
        WoW über Battle.net starten - derselbe Weg wie bis 1.7.

        `manager.start_wow()` und nicht `manager.launcher`: der
        `Launcher` startet eine *Datei* (er gehört dem Selbstupdate und
        verlangt einen Pfad), Battle.net startet der
        `BattleNetLauncher`. Der Aufruf `launcher.launch()` ohne
        Argument warf deshalb nur einen `TypeError`, den das
        `except Exception` darunter verschluckt hat - der Knopf ist
        stillschweigend immer in den Einstellungen gelandet, statt das
        Spiel zu starten.
        """

        #
        # Unter Linux ist oft noch kein Startbefehl hinterlegt - dann
        # ist der richtige nächste Schritt die Einstellung, nicht eine
        # Fehlermeldung.
        #

        if (
            is_linux()
            and not self.manager.config.get_linux_launch_command()
        ):

            self.manager.logger.warning(
                "Kein Battle.net-Start-Befehl hinterlegt - bitte "
                "zuerst in den Einstellungen (WoW-Client) einrichten."
            )

            self.openSettingsSection.emit("wow_client")

            return

        #
        # Fehler meldet start_wow() selbst ins Protokoll.
        #

        self.manager.start_wow()

    def _open_url(self, url: str):
        """
        Über `core.browser.open_url()` - und nicht mehr über ein
        blankes `webbrowser.open()`.

        Das war die Ursache dafür, dass dieser Knopf nichts tat: im
        AppImage erbt der Browser sonst unser eigenes
        `LD_LIBRARY_PATH` und stirbt beim Start, ohne dass hier eine
        Ausnahme ankommt. Die beiden anderen Aufrufer im Programm
        hatten den Schutz, dieser eine nicht.

        Ein Discord-Link geht zuerst an die Discord-Anwendung: im
        Browser landete man in einer zweiten, meist abgemeldeten
        Ansicht desselben Servers, während die Anwendung daneben
        offen stand. Gibt es für das Schema kein Programm, übernimmt
        weiterhin der Browser (siehe `core/browser.py`).
        """

        open_url(url, self.manager.logger, app_url(url))

    # --------------------------------------------------
    # Updates
    # --------------------------------------------------

    def set_update_runner(self, runner):
        """
        Duck-getypt vom MainWindow gesetzt (`_ensure_page`).

        **Ein** Läufer für die ganze Anwendung, nicht einer je Seite:
        sonst könnte hier ein Addon-Update starten, während die Seite
        "Addon & Updates" nichts davon weiß und ein zweites anwirft.
        """

        self._runner = runner

        runner.started.connect(self._on_update_started)

        runner.finished.connect(self._on_update_finished)

    def _start_update(self, component: str):

        if self._runner is None:
            return

        if component == ADDON:

            self._runner.install_addon()

            return

        self._runner.update_companion()

    def _open_changelog(self, component: str):

        show_changelog(self.manager.state, component, self)

    def _on_update_started(self, component: str):

        row = self.updates.rows.get(component)

        if row is None:
            return

        row.set_running(
            True,
            "Wird heruntergeladen und installiert …"
            if component == COMPANION
            else "Wird heruntergeladen - vorher wird eine Sicherung "
            "angelegt.",
        )

    def _on_update_finished(self, component: str, success: bool, message: str):

        row = self.updates.rows.get(component)

        if row is not None:

            row.set_running(
                False,
                message if not success else "",
            )

        #
        # Nach einem Addon-Update sind Fassung und Zustand andere -
        # die Seite zeichnet sich deshalb neu, statt auf den nächsten
        # Seitenwechsel zu warten.
        #

        if success:
            self.refresh()

    def _refresh_updates(self):
        """
        Die Karte an den Zustand anlegen.

        Der Auszug kommt aus `core/changelog_source.py` und damit aus
        derselben Quelle wie die vollständige Ansicht - was hier in
        drei Zeilen steht, findet sich dort wieder.
        """

        state = self.manager.state

        pending = []

        if state.update_available:

            pending.append((
                ADDON,
                state.addon_version if state.addon_found else "",
                state.github_version,
            ))

        if state.companion_update_available:

            pending.append((
                COMPANION,
                state.companion_version,
                state.companion_latest_version,
            ))

        self.updates.setVisible(bool(pending))

        if not pending:
            return

        self.updates.setCount(len(pending))

        waiting = {component for component, _i, _a in pending}

        for component, installed, available in pending:

            row = self.updates.rows[component]

            row.setVisible(True)

            note = update_note(component, state)

            row.apply(
                LABELS[component],
                installed,
                available,
                _excerpt(note, installed),
                _note_head(note, installed),
            )

        for component, row in self.updates.rows.items():

            if component not in waiting:
                row.setVisible(False)

    # --------------------------------------------------

    def _tick(self):
        """
        Der Minutentakt: Begrüßung und Fusszeile.

        Hängt allein an der Uhr und liest keine neuen Daten - was hier
        passiert, ist Zeichnen und nichts sonst.
        """

        self._refresh_greeting()

        self.tasks.apply(self._build_tasks(), self._checked_text())

    def _user_name(self) -> str:
        """
        Wen die Anwendung grüßt.

        Erste Wahl ist der **im Spiel angemeldete Charakter**: den
        meldet das Addon seit WeintCodex 1.3.3.0 von sich aus (siehe
        `core/character_report_sync.py`) und er ist die einzige
        Antwort, die niemand geraten hat. Bewusst *nicht*
        `academy_player_name` - das ist die Auswahl der Academy und
        kann auf einem Kollegen stehen, dessen Zahlen man sich einmal
        angesehen hat.

        Danach der Discord-Name, der ohnehin unten in der Navigation
        steht. Ist auch der nicht bekannt, grüßt die App ohne Namen,
        statt sich einen zu suchen.
        """

        config = getattr(self.manager, "config", None)

        if config is not None:

            name = str(
                config.data.get("academy_ingame_character", "") or ""
            ).strip()

            if name:
                return name

        store = getattr(self.manager, "discord_account", None)

        if store is not None:

            try:
                account = store.load()

            except Exception:

                #
                # Eine unlesbare discord_account.json ist kein Grund,
                # gar nicht mehr zu grüßen.
                #

                account = None

            if account:

                name = str(account.get("username", "") or "").strip()

                if name:
                    return name

        state = getattr(self.manager, "state", None)

        name = str(getattr(state, "discord_name", "") or "").strip()

        #
        # "-" ist der Anfangswert von `AppState.discord_name` und
        # heißt "nicht bekannt", nicht "so heißt der Nutzer".
        #

        return "" if name in ("", "-") else name

    def _refresh_greeting(self):
        """
        Rubrik und Titel - die beiden Zeilen im Kopf.

        Welcher Satz dasteht, entscheidet `core/greeting.py`; hier
        wird er nur gesetzt. Die Trennung ist dieselbe wie bei
        `roster_target()`: die Entscheidung ist prüfbar, ohne ein
        Fenster zu bauen.
        """

        state = self.manager.state

        self.header.setEyebrow(greeting(self._user_name()))

        self.header.setTitle(
            headline(
                addon_update=state.update_available,
                app_update=state.companion_update_available,
                wow_found=state.wow_found,
            )
        )

    # --------------------------------------------------
    # Erneut nach Updates sehen
    # --------------------------------------------------

    def check_updates(self):
        """
        Beide Update-Kanäle noch einmal gegen GitHub prüfen.

        In einem eigenen kurzlebigen Thread - wie bei
        `ConnectionsPage.sync_now()` und den Archiv-Abrufen. Die
        Prüfung geht zweimal ins Netz, und das gehört nicht in einen
        Klick-Handler: das Fenster stünde für die Dauer still.

        Die Anzeige zieht danach von selbst nach, weil
        `refresh_update_status()` am Ende `state_changed` meldet und
        das Fenster daraufhin die sichtbare Seite neu zeichnet - hier
        wird deshalb nichts direkt aktualisiert.
        """

        if self._check_thread is not None and self._check_thread.is_alive():

            #
            # Zweimal drücken soll nicht zwei Durchgänge starten.
            #

            return

        self.manager.logger.info("Prüfe GitHub auf neue Versionen...")

        self.check_button.setEnabled(False)

        self.check_button.setText("Wird geprüft …")

        self._check_thread = threading.Thread(
            target=self._check_worker,
            daemon=True,
            name="OverviewUpdateCheck",
        )

        self._check_thread.start()

    def _check_worker(self):

        try:

            self.manager.refresh_update_status()

            self.manager.logger.success("GitHub erfolgreich geprüft.")

        except Exception as exc:

            self.manager.logger.error(
                f"Update-Prüfung fehlgeschlagen: {exc}"
            )

        finally:

            self.checkFinished.emit()

    def _on_check_finished(self):

        self.check_button.setEnabled(True)

        self.check_button.setText("Erneut prüfen")

    # --------------------------------------------------

    def on_enter(self):

        self._clock.start()

        #
        # Den Spielstand lesen - im Hintergrund und nur, wenn er sich
        # geändert hat (siehe `gui/controllers/inventory_loader.py`).
        # Hier und nicht in `refresh()`: das darf nur zeichnen.
        #

        self.loader.request()

    def _on_inventory(self, inventory):

        self.gold.apply(inventory)

    def on_leave(self):

        self._clock.stop()

    # --------------------------------------------------

    def _open_inventory(self):

        from gui.navigation import PageId

        self.pageRequested.emit(PageId.INVENTORY)

    def _open_addon_changelog(self):

        self._open_changelog(ADDON)

    def _codex_action(self):
        """
        Der dritte Knopf der Codex-Karte: ohne Spielordner in die
        Einstellung, ohne Addon zur Installation.
        """

        if not self.manager.state.wow_found:

            self.openSettingsSection.emit("wow_client")

            return

        self._open_addon_page()

    def _open_addon_page(self):
        """
        Zu "Addon & Updates" - dorthin, wo Installation, Update und
        Sicherungen tatsächlich stattfinden.
        """

        from gui.navigation import PageId

        self.pageRequested.emit(PageId.ADDON)

    def _open_characters(self):

        from gui.navigation import PageId

        self.pageRequested.emit(PageId.CHARACTERS)

    # --------------------------------------------------

    def on_layout_changed(self, state):
        """
        Unter 980 px stehen Codex-Karte und Aufgaben untereinander.

        Duck-getypt vom MainWindow aufgerufen, genau wie on_enter und
        on_leave.
        """

        if state.single_column == self._single_column:
            return

        self._single_column = state.single_column

        self.row.removeItem(self.side)

        if state.single_column:

            self.row.setColumnMinimumWidth(1, 0)

            self.row.addLayout(self.side, 1, 0)

        else:

            self.row.setColumnMinimumWidth(1, 386)

            self.row.addLayout(self.side, 0, 1)

    def refresh(self):

        state = self.manager.state

        self.codex.apply(state, update_note(ADDON, state), addon_history(state))

        #
        # Charaktere aus der Charakterliste, Gold aus dem zuletzt
        # gelesenen Bestand - beides lokal, `refresh()` darf nicht ins
        # Netz und nicht an Dateien (siehe
        # `tests/test_update_visibility.py`).
        #

        store = getattr(self.manager, "characters", None)

        if store is not None:

            try:
                self.characters.apply(store.characters())

            except Exception:
                self.characters.apply([])

        self.gold.apply(self.loader.inventory)

        self._refresh_updates()

        self.bridges.apply(
            self.manager.state,
            self._last_sync_text(),
        )

        #
        # Die Aufgabenliste zuletzt vor dem Kopf: sie liest den
        # Zustand, den die Karten darüber gerade gesetzt haben, und
        # fasst ihn zu dem zusammen, was daraus für den Nutzer folgt.
        #

        self.tasks.apply(
            self._build_tasks(),
            self._checked_text(),
        )

        #
        # Zuletzt der Kopf: er fasst zusammen, was die Karten darunter
        # im einzelnen zeigen, und liest dafür denselben Zustand.
        #

        self._refresh_greeting()

    # --------------------------------------------------
    # Was jetzt zu tun ist
    # --------------------------------------------------

    def _build_tasks(self) -> list:
        """
        Die Aufgabenliste aus dem bereits gelesenen Zustand.

        **Kein Netzzugriff.** Diese Methode läuft aus `refresh()`, und
        `refresh()` darf nur zeichnen (siehe
        `tests/test_update_visibility.py` und
        `docs/architecture/navigation.md`). Alles hier stammt aus
        `manager.state` und den lokalen Speichern.

        Aufgenommen wird nur, wogegen sich etwas tun lässt - siehe den
        Modulkommentar von `gui/widgets/task_card.py`. Eine Störung
        beim Bot steht deshalb nicht hier, sondern unter
        "Verbindungen".
        """

        state = self.manager.state

        tasks = []

        #
        # Ohne Addon gibt es nichts zu messen, nichts zu melden und
        # nichts zu sichern. Es steht deshalb ganz oben und als
        # einzige Aufgabe auf "blockierend".
        #

        if not state.addon_found:

            tasks.append(Task(
                key="addon-missing",
                title="WeintCodex ist nicht installiert",
                detail=(
                    "Ohne das Addon im Spiel bleiben Auswertung, "
                    "Vorbereitung und Charakterliste leer."
                ),
                action="Jetzt installieren",
                on_action=self._open_addon_page,
                urgency=URGENCY_BLOCKING,
                icon="software",
            ))

        elif state.update_available:

            tasks.append(Task(
                key="addon-update",
                title="Addon-Update verfügbar",
                detail=(
                    f"{state.addon_version} → {state.github_version}"
                ),
                action="Jetzt aktualisieren",
                on_action=self._open_addon_page,
                urgency=URGENCY_DUE,
                icon="download",
            ))

        if state.companion_update_available:

            tasks.append(Task(
                key="companion-update",
                title="Neue Fassung der App",
                detail=(
                    f"{state.companion_version} → "
                    f"{state.companion_latest_version}"
                ),
                action="Ansehen",
                on_action=self._open_addon_page,
                urgency=URGENCY_IDLE,
                icon="companion",
            ))

        #
        # Ohne Discord bleibt alles nutzbar, was den eigenen Rechner
        # betrifft - der Termin, die Aufstellung und die Auswertung
        # kommen aber von dort. Deshalb eine Aufgabe und keine
        # Störung.
        #

        if not state.discord_connected:

            tasks.append(Task(
                key="discord",
                title="Discord ist nicht verknüpft",
                detail=(
                    "Twinkliste, Charakterzuordnung und Gilden-"
                    "Kalender kommen über den Bot."
                ),
                action="Verbinden",
                on_action=lambda: self.openSettingsSection.emit("discord"),
                urgency=URGENCY_DUE,
                icon="discord",
            ))

        tasks.extend(self._character_tasks())

        return tasks

    def _character_tasks(self) -> list:
        """
        Die Aufgaben, die aus der Charakterliste folgen.

        Eigene Methode, weil sie als einzige einen Speicher braucht,
        der fehlen kann: `CharacterStore` wird vom CompanionManager
        aufgebaut, und die Seite wird gebaut, bevor er fertig ist.
        """

        store = getattr(self.manager, "characters", None)

        if store is None:
            return []

        try:
            summary = store.preparation_summary()

        except Exception:

            #
            # Eine unlesbare characters.json ist kein Grund, die ganze
            # Aufgabenliste ausfallen zu lassen.
            #

            return []

        tasks = []

        #
        # Noch kein Charakter gemeldet: das ist keine offene
        # Vorbereitung, sondern eine fehlende Anmeldung im Spiel. Der
        # Unterschied ist der zwischen "du hast etwas zu tun" und "das
        # erledigt sich beim nächsten Einloggen von selbst".
        #

        if not summary.get("characters"):

            if self.manager.state.addon_found:

                tasks.append(Task(
                    key="characters-empty",
                    title="Noch kein Charakter gemeldet",
                    detail=(
                        "Melde dich im Spiel einmal an - danach steht "
                        "dein Charakter hier."
                    ),
                    action="Charaktere öffnen",
                    on_action=self._open_characters,
                    urgency=URGENCY_IDLE,
                    icon="charaktere",
                ))

            return tasks

        #
        # Seit 5.1 (Forever) keine "offene Vorbereitung" mehr - die
        # zählte Verzauberungen und Sockel, die es dort nicht gibt.
        # Was WeintCodex Forever meldet, sind leere Plätze und
        # zerbrochene Gegenstände; ein zerbrochener Gegenstand ist
        # etwas, das man vor dem nächsten Abend tatsächlich tut.
        #

        try:
            characters = store.characters()

        except Exception:
            characters = []

        broken = [
            sheet.get("name", "?")
            for sheet in characters
            if any(
                issue.get("status") == "wrong"
                for issue in (sheet.get("issues") or [])
            )
        ]

        if broken:

            tasks.append(Task(
                key="repair",
                title=(
                    "Ausrüstung zerbrochen"
                    if len(broken) == 1
                    else f"Ausrüstung zerbrochen bei {len(broken)} Charakteren"
                ),
                detail=", ".join(broken[:4]) + " - beim nächsten Händler reparieren.",
                action="Charaktere öffnen",
                on_action=self._open_characters,
                urgency=URGENCY_DUE,
                icon="charaktere",
            ))

        return tasks

    @staticmethod
    def _ago(at: float) -> str:
        """
        Ein Zeitpunkt als Abstand zu jetzt, grobkörnig.

        `0.0` heisst "noch nie" und liefert einen leeren String - die
        Aufrufer schreiben dafür ihren eigenen Satz. Eine Null als
        Uhrzeit zu lesen wäre dieselbe Verwechslung wie `at == -1` im
        Analyzer.

        Grobkörnig, weil die Fusszeile im Minutentakt nachgezogen wird
        (siehe `self._clock`): eine Sekundenangabe stünde dort
        zwischen zwei Zeichnungen fast immer falsch.
        """

        if not at:
            return ""

        seconds = max(0, int(time.time() - at))

        if seconds < 90:
            return "gerade eben"

        minutes = seconds // 60

        if minutes < 60:
            return f"vor {minutes} min"

        hours = minutes // 60

        if hours < 24:
            return f"vor {hours} Std"

        return f"vor {hours // 24} Tagen"

    def _checked_text(self) -> str:
        """
        Die Fusszeile der Aufgabenkarte.

        Sie nennt den Zeitpunkt der letzten Prüfung und nicht "alles in
        Ordnung": eine Liste, die leer ist, weil noch nichts geprüft
        wurde, sieht sonst aus wie eine, die nichts gefunden hat.
        """

        checked = self._ago(
            getattr(self.manager.state, "last_check_at", 0.0)
        )

        if not checked:
            return "NOCH NICHT GEPRÜFT"

        return f"ZULETZT GEPRÜFT {checked}"

    def _last_sync_text(self) -> str:

        return self._ago(
            getattr(self.manager.state, "last_sync_at", 0.0)
        )
