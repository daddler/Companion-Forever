"""
WeintCompanion 5 - Forever Edition
Design-Tokens, Palette "Graphit"

Die einzige Stelle im Programm, an der ein Farbwert steht.

Der Entwurf zu 2.0 beschreibt jede Fläche, jeden Abstand und jede
Schrift über einen Namen; dieser Name ist hier definiert und wird
danach ausschließlich als Name verwendet - im Stylesheet ebenso wie in
den gemalten Widgets. Vor 2.0 lagen dieselben Werte in `colors.py`,
`metrics.py`, `typography.py`, in `styles_old.py` und zusätzlich als
Literale in einzelnen Widgets. Ein Akzentwechsel zur Laufzeit war
dadurch nicht möglich, denn niemand wusste, wo überall Bernstein steht.

Dieses Modul importiert bewusst **kein Qt**. Es ist reine Datenhaltung
und damit ohne laufende Oberfläche testbar - dieselbe Trennung, die
`analyzer/` von der GUI freihält. Alles, was eine QFont, eine QColor
oder einen QPainter braucht, steht in `fonts.py`, `icons.py` oder im
Widget selbst.

WAS SICH MIT 5.0 GEÄNDERT HAT
-----------------------------

Die **Schichtung bleibt**: Tiefe entsteht durch hellere Flächen und
eine 1-px-Oberkante, nicht durch Rahmen oder Schatten. Was sich
ändert, sind die Werte darin.

* Der Grund ist streng neutral und eine Spur kühl (#0C0C0F statt des
  bräunlich getönten #0A0A0C). Der Grund dafür steht im Bild selbst:
  fast alle Farbe darin kommt von den Klassenfarben, und ein warmer
  Grund zieht an ihnen.
* Der Akzent ist **einer**, und er trägt ausschliesslich Bedeutung.
  Die Leitidee bis 4.0 war "Bernstein trägt die Bedeutung, Violett
  nur das Licht" - zwei Farbbegriffe, von denen einer nichts
  bedeutete. Das Flächenlicht ist ersatzlos weg; was übrig bleibt,
  ist `ACCENTS`.
* Violett ist die Voreinstellung. In WoW ist es keine besetzte
  Bedeutungsfarbe und liegt neben keiner der neun Klassenfarben -
  Bernstein lag neben Krieger und Schurke.
* Drei Schriften statt zwei: eine Serifen-Display-Schrift für
  Überschriften, eine humanistische Grotesk für alles Bedienbare,
  eine Monospace für Zahlen und Rubriken.

Der Akzent färbt Navigationsmarke, Hauptknopf, Fortschritt, Sterne,
Rubriklabel im Handlungskontext und Fokusrahmen. Sonst nichts -
deshalb bleibt die Oberfläche grau, auch wenn der Akzent wechselt.
"""

from __future__ import annotations

from dataclasses import dataclass


# ==========================================================
# Flächen, Rahmen, Text
# ==========================================================

#
# Höhe entsteht in diesem Entwurf nicht durch Rahmen und nicht durch
# Schatten, sondern durch Schichtung: eine Fläche steht über der
# nächsten, weil sie heller ist und eine 1 px helle Oberkante trägt.
# Die Reihenfolge base < card < raised ist deshalb keine Willkür,
# sondern die Staffelung selbst - `sunken` liegt unter `base`.
#

SURFACE = {
    "base": "#0C0C0F",      # Fenstergrund, Inhaltsfläche
    "card": "#141419",      # Karte, Kachel
    "sunken": "#08080A",    # Navigationsspalte, Titelleiste, Balkenrinne
    "raised": "#1C1C23",    # Hover, aktiver Navigationseintrag, Sekundärknopf
}

BORDER = {
    "base": "#26262E",
    "strong": "#33333C",

    #
    # Die schwächste der drei: Rinnen, gesperrte Knöpfe, der Rahmen um
    # eine Segmentleiste. Sie soll die Fläche gliedern, ohne selbst
    # eine Kante zu behaupten.
    #
    "faint": "#1E1E25",
}

#
# Die 1-px-Oberkante jeder Karte. Sie ersetzt den Schatten und wird als
# linearer Verlauf von oben gemalt, nicht als Rahmen: ein umlaufender
# Rahmen ist genau das, was der Entwurf vermeiden will.
#

EDGE_TOP = "rgba(255,255,255,0.07)"

#
# Die Kartenfläche selbst ist ein senkrechter Verlauf (oben heller).
# Auch das ersetzt den Schatten - eine gleichmäßig gefüllte Karte wirkt
# flach, sobald ihr der Rahmen fehlt.
#

CARD_GRADIENT = ("#17171C", "#101014")

#
# Variante `accent` derselben Karte (Entwurf §5): nur für die eine
# Karte pro Ansicht, die eine Handlung trägt.
#

CARD_GRADIENT_ACCENT = ("#17161F", "#101014")

#
# Die eine hervorgehobene Kachel im Bewertungsraster der Academy
# (§6.3): der schwächste Bereich bekommt eine in Richtung Fehlerfarbe
# gezogene Fläche, damit er sich von den fünf neutralen Kacheln
# absetzt, ohne dass die Fläche selbst schon rot wäre - das bleibt der
# Oberkante vorbehalten.
#

CARD_GRADIENT_WEAKEST = ("#1C1419", "#121016")

TEXT = {
    "primary": "#EDEDF2",
    "secondary": "#A0A0AC",
    "muted": "#8A8A98",
    "faint": "#5F5F6B",
    "onAccent": "#14121C",   # Text auf der Akzentfläche
}

WHITE = "#FFFFFF"

BLACK = "#000000"

#
# Einzelne Flaechen, die zwischen den Stufen von SURFACE liegen. Sie
# stehen hier und nicht im jeweiligen Widget, weil sonst genau das
# entstuende, was das Abnahmekriterium verbietet: ein Farbwert
# ausserhalb dieser Datei - und damit eine Flaeche, die bei einer
# Aenderung der Palette uebersehen wird.
#

SURFACE_EXTRA = {
    #
    # Die Systemzeile der Uebersicht: eine Spur unter der Karte, damit
    # sie sich als Fuss und nicht als weitere Karte liest.
    #
    "row": "#101014",

    #
    # Oberkante des Titelleistenverlaufs (nach `sunken` hin).
    #
    "titleBar": "#101014",

    #
    # Flaeche eines Meldungsstreifens - identisch mit der Oberkante
    # des Kartenverlaufs, damit ein Toast wie eine angehobene Karte
    # wirkt.
    #
    "toast": "#17171C",

    #
    # Der helle Punkt im Schimmer eines Skeletts.
    #
    "shimmer": "#1E1E25",

    #
    # Mitte des radialen Verlaufs im Startbildschirm - die einzige
    # Flaeche, die einen Hauch des Violetts als Grundton traegt.
    #
    "splash": "#14121C",
}


# ==========================================================
# Startbildschirm-Artwork
# ==========================================================

#
# Die Farben des Startbild-Ladebalkens gehören zum **Bild**, nicht zum
# Theme: das Artwork (assets/splash.png) trägt seinen eigenen goldenen
# Rahmen und ein grünes Leuchten, und der echte Balken liegt genau auf
# dem gemalten. Er darf deshalb NICHT dem wählbaren Akzent folgen -
# sonst steht ein bernsteinfarbener Balken in einem grün gemalten
# Rahmen. Aus demselben Grund wie `wow_colors.py` eine eigene Tabelle,
# aber weiterhin hier: ausserhalb von tokens.py steht kein Hex-Wert.
#

SPLASH_ART = {
    #
    # Der Zierrahmen um den Balken.
    #
    "frame": "#C9A227",

    #
    # Die dunkle Rinne darunter - deckt den gemalten Balken ab, damit
    # ein leerer Fortschritt nicht den vollen aus dem Bild zeigt.
    #
    "trough": "#0B0A08",

    #
    # Der Verlauf der Füllung, von links nach rechts.
    #
    "fillFrom": "#4C7A16",
    "fillTo": "#9BE023",

    #
    # Das Leuchten über der Füllung.
    #
    "glow": "#C6F76A",
}


# ==========================================================
# Akzent
# ==========================================================

#
# Drei wählbare Varianten. Der Akzent färbt **ausschließlich**: aktiven
# Navigationsindikator und -symbol, Hauptknopf, Fortschrittsbalken und
# -ring, Sterne, Rubriklabel im Handlungskontext, Countdown-Chip und
# Fokusrahmen. Alles andere bleibt neutral - sonst wird aus einem
# Akzent eine zweite Grundfarbe.
#
# `onBase` ist die Textfarbe **auf** der Akzentfläche und gehört
# deshalb zur Variante, nicht zu TEXT: Stahl ist so hell, dass darauf
# derselbe dunkle Ton steht wie auf Violett, Aqua verlangt einen
# eigenen.
#
# Violett ist die Voreinstellung, und zwar aus einem Grund, der mit
# Geschmack nichts zu tun hat: es ist in WoW keine besetzte
# Bedeutungsfarbe und liegt neben keiner der neun Klassenfarben. Der
# Bernstein der Vorgängerfassung lag zwischen Krieger (#C79C6E) und
# Schurke (#FFF569) - in einer Aufstellung war er dadurch eine
# vierzehnte Klassenfarbe.
#

ACCENTS = {
    "violet": {"base": "#7C6CFF", "light": "#8B7BFF", "onBase": "#14121C"},
    "aqua": {"base": "#2DD4BF", "light": "#5FE3D2", "onBase": "#041613"},
    "steel": {"base": "#D4D4DC", "light": "#E6E6EC", "onBase": "#14121C"},
}

ACCENT_DEFAULT = "violet"

#
# Knopfverläufe je Zustand, abgeleitet aus der Akzentvariante. Der
# Entwurf nennt sie für Bernstein ausdrücklich (§5); für die beiden
# anderen Varianten entstehen sie nach derselben Regel: Ruhe geht von
# `light` nach `base`, Überfahren liegt eine Spur heller, Gedrückt ist
# flach und dunkler.
#

ACCENT_PRESSED = {
    "violet": "#5D4FE0",
    "aqua": "#1FA898",
    "steel": "#A9A9B4",
}

ACCENT_HOVER = {
    "violet": ("#9F92FF", "#8B7BFF"),
    "aqua": ("#7DEBDD", "#3FDCC8"),
    "steel": ("#F2F2F6", "#D8D8E0"),
}


def accent(name: str | None = None) -> dict:
    """
    Die Akzentvariante zu `name`, mit Rückfall auf die Voreinstellung.

    Ein unbekannter Name darf die Oberfläche nicht farblos lassen -
    er kann aus einer von Hand bearbeiteten `config.json` stammen.
    """

    return ACCENTS.get(name or "", ACCENTS[ACCENT_DEFAULT])


# ==========================================================
# Bedeutungsfarben
# ==========================================================

#
# In allen drei Akzenten identisch. Das ist der Punkt: der Akzent ist
# Geschmack, die Bedeutung ist es nicht. Wer Jade wählt, soll einen
# Fehler weiterhin an Rot erkennen.
#
# `empty` ist absichtlich None - ein leerer Statuspunkt wird nicht
# gefüllt, sondern nur als 1-px-Kontur gezeichnet. Ein grauer Punkt
# sähe aus wie ein Zustand, "keine Angabe" ist aber keiner.
#

STATE = {
    "ok": "#34C77B",
    "warn": "#F0A63A",
    "error": "#F46366",
    "live": "#F46366",     # pulsierend
    "info": "#4EA8F5",
    "empty": None,
}

STATE_EMPTY_OUTLINE = "#5F5F6B"

#
# Textfarbe auf getönter Fläche. Die Grundfarbe aus STATE ist als
# Schrift auf dunklem Grund zu dunkel; diese Werte sind die aufgehellte
# Entsprechung.
#

STATE_TEXT = {
    "ok": "#34C77B",
    "warn": "#F0A63A",
    "error": "#F88C8B",
    "info": "#4EA8F5",
}

#
# Getönte Chip-Flächen (§2.3): Grundfarbe mit 12-14 % Deckkraft,
# 1-px-Rahmen mit 34-42 % derselben Farbe. Als Konstanten, damit nicht
# jedes Widget seinen eigenen Wert in diesem Korridor wählt.
#

TINT_SURFACE = 0.13
TINT_BORDER = 0.38


# ==========================================================
# Raum und Radius
# ==========================================================

#
# space.1 ... space.7 - im Code als SPACE[0] ... SPACE[6].
#

SPACE = [4, 8, 12, 16, 24, 32, 48]

RADIUS = {
    "sm": 6,
    "md": 10,
    "lg": 14,
    "xl": 20,
    "pill": 999,
}


# ==========================================================
# Dichte
# ==========================================================

#
# Gilt global (eine Einstellung), nicht pro Ansicht: zwei Ansichten mit
# unterschiedlicher Zeilenhöhe nebeneinander lesen sich wie zwei
# Programme.
#
# `font_delta` verschiebt jede Schriftgröße um diesen Betrag. Deshalb
# steht er hier und nicht in TYPE - die Schriftgrößen sind absolut, die
# Dichte verschiebt sie.
#

DENSITY = {
    "comfortable": {
        "row": 24,
        "pad_v": 16,
        "pad_h": 20,
        "gap": 20,
        "btn": 40,
        "btn_sm": 34,
        "nav_item": 40,
        "title_bar": 40,
        "font_delta": 0,
    },
    "compact": {
        "row": 20,
        "pad_v": 12,
        "pad_h": 16,
        "gap": 14,
        "btn": 34,
        "btn_sm": 30,
        "nav_item": 34,
        "title_bar": 36,
        "font_delta": -1,
    },
}

DENSITY_DEFAULT = "comfortable"


def density(name: str | None = None) -> dict:
    """
    Die Dichte zu `name`, mit Rückfall auf die Voreinstellung.
    """

    return DENSITY.get(name or "", DENSITY[DENSITY_DEFAULT])


# ==========================================================
# Typografie
# ==========================================================

#
# Drei Familien, drei Aufgaben - siehe `gui/theme/fonts.py` für die
# Dateien und ihre Anmeldung.
#
# `FAMILY_DISPLAY` ist neu in 5.0 und ersetzt Inter im Überschriften-
# bereich. Der Grund ist nicht Geschmack, sondern Aufgabe: eine
# Überschrift steht einmal auf der Seite und soll Charakter haben,
# eine Beschriftung steht dreissigmal und soll dicht und ruhig sein.
# Beides von derselben Schrift verlangt zu haben war der Kompromiss,
# den die Vorgängerfassung geschlossen hat.
#

FAMILY_DISPLAY = "Newsreader"

FAMILY_SANS = "IBM Plex Sans"

FAMILY_MONO = "IBM Plex Mono"


@dataclass(frozen=True)
class TypeToken:
    """
    Eine benannte Schriftrolle.

    `letter_spacing` ist in em angegeben, wie im Entwurf. Qt kennt
    `letter-spacing` im Stylesheet **nicht** und verwirft die Angabe
    wortlos - die Umrechnung in Pixel und das Setzen über
    `QFont.setLetterSpacing` passieren deshalb in `fonts.py`.
    """

    family: str

    size: int

    weight: int

    letter_spacing: float = 0.0

    uppercase: bool = False

    italic: bool = False


TYPE = {

    #
    # Display: die Serifenschrift. Drei Stufen, weil es drei
    # Überschriftenränge gibt - die Begrüssung der Übersicht, die
    # Überschrift einer Seite, der eine grosse Satz in einer Karte.
    #

    "display": TypeToken(FAMILY_DISPLAY, 38, 500, -0.015),
    "displayPage": TypeToken(FAMILY_DISPLAY, 30, 500, -0.01),
    "displayCard": TypeToken(FAMILY_DISPLAY, 23, 500),

    #
    # Die kursive Fortsetzung einer Display-Zeile ("Heute ist Raid.
    # *Noch zwei Stunden.*"). Als eigene Rolle und nicht als
    # `italic=True` am Aufrufer: die Kursive ist im Entwurf ein
    # Bedeutungsträger (der Nachsatz, nicht die Hauptsache) und
    # steht deshalb hier, wo sie benannt ist.
    #

    "displayQuiet": TypeToken(FAMILY_DISPLAY, 38, 400, -0.015, italic=True),

    #
    # `title` bleibt als Name bestehen - er steht an gut hundert
    # Stellen. Er ist jetzt die Seitenüberschrift.
    #

    "title": TypeToken(FAMILY_DISPLAY, 30, 500, -0.01),

    "section": TypeToken(FAMILY_SANS, 17, 600),
    "card": TypeToken(FAMILY_SANS, 15, 600),
    "body": TypeToken(FAMILY_SANS, 13, 400),
    "small": TypeToken(FAMILY_SANS, 12, 400),
    "ui": TypeToken(FAMILY_SANS, 13, 500),

    "mono": TypeToken(FAMILY_MONO, 12, 600),
    "monoBig": TypeToken(FAMILY_MONO, 34, 600, -0.02),
    "eyebrow": TypeToken(FAMILY_MONO, 11, 500, 0.18, uppercase=True),
    "micro": TypeToken(FAMILY_MONO, 10, 400, 0.14, uppercase=True),
}

#
# Gewichte als Namen, damit Widgetcode keine nackten Zahlen setzt.
#

WEIGHT = {
    "normal": 400,
    "medium": 500,
    "semibold": 600,
    "bold": 700,
}


# ==========================================================
# Fenster
# ==========================================================

#
# Entwurfsgröße 1440 x 900, geprüft 1120 x 720, Minimum 960 x 640.
# Vor 2.0 stand das Minimum auf 1500 x 900 - auf einem 1366er
# Bildschirm ließ sich das Fenster damit nicht vollständig anzeigen.
#

WINDOW_DEFAULT = (1440, 900)

WINDOW_MIN = (960, 640)

NAV_WIDTH_EXPANDED = 232

NAV_WIDTH_COLLAPSED = 72

#
# Haltepunkte (§4). Die Hysterese verhindert, dass ein Fenster, das
# genau auf der Kante steht, bei jedem Pixel Mausbewegung hin- und
# herschaltet.
#

BREAKPOINT_DRAWER = 1280

BREAKPOINT_NAV = 1120

BREAKPOINT_SINGLE_COLUMN = 980

BREAKPOINT_HYSTERESIS = 40


# ==========================================================
# Hilfsfunktionen
# ==========================================================

def rgb(value: str) -> tuple[int, int, int]:
    """
    "#RRGGBB" -> (r, g, b).
    """

    value = value.lstrip("#")

    if len(value) == 3:
        value = "".join(c * 2 for c in value)

    if len(value) != 6:
        raise ValueError(f"Kein sechsstelliger Hex-Wert: {value!r}")

    return (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
    )


def tint(value: str, alpha: float) -> str:
    """
    Eine Farbe mit Deckkraft, als `rgba(...)` für Qt-Stylesheets.

    Die eine Stelle, an der aus einem Hex-Wert eine transparente Farbe
    wird. Ohne sie stünde in jedem Widget, das eine getönte Chip-Fläche
    braucht, eine eigene handgeschriebene rgba-Zeichenkette - und damit
    wieder ein Farbwert außerhalb dieser Datei.
    """

    red, green, blue = rgb(value)

    return f"rgba({red},{green},{blue},{alpha:.3f})"


def mix(foreground: str, background: str, amount: float) -> str:
    """
    Zwei Farben mischen, `amount` ist der Anteil von `foreground`.

    Gebraucht, wo eine transparente Farbe nicht reicht, weil das
    Ergebnis gemalt und nicht überlagert wird (Sparkline auf Karte,
    Balkenfüllung in der Rinne).
    """

    a = rgb(foreground)
    b = rgb(background)

    amount = max(0.0, min(1.0, amount))

    parts = [
        round(a[i] * amount + b[i] * (1.0 - amount))
        for i in range(3)
    ]

    return "#%02X%02X%02X" % tuple(parts)
