"""
WeintCompanion 5 - Forever Edition
Schriften

Zwei Dinge, die bis 1.7 stillschweigend nicht funktioniert haben und
hier zusammen geloest werden.

**Erstens: die Schriften lagen der App nicht bei.** Das Stylesheet
nannte Familien, von denen keine Datei im Programm enthalten war.
Qt loest einen unbekannten Familiennamen nicht mit einem Fehler auf,
sondern wortlos gegen die naechstbeste Systemschrift. Auf einem
Entwicklerrechner, auf dem Inter installiert ist, sah alles richtig
aus; auf dem Rechner eines Raiders sah es anders aus, ohne dass
irgendwo etwas gemeldet worden waere. Seit 2.0 liegen beide Familien
unter `assets/fonts/` und werden hier registriert.

**Zweitens: die Laufweite wirkte nie.** Der Entwurf sperrt die kleinen
Rubriklabels weit (0.18em bei 11 px, 0.16em bei 10 px) - genau das gibt
ihnen ihren Charakter. `letter-spacing` ist aber **keine Eigenschaft,
die Qt in Stylesheets kennt**; sie wurde bei jedem `setStyleSheet`
kommentarlos verworfen. Gesetzt wird sie nur ueber
`QFont.setLetterSpacing`, und genau das passiert in `font()`.

Die Umrechnung: `QFont.AbsoluteSpacing` erwartet Pixel, der Entwurf
nennt em. Ein em ist die Schriftgroesse, also 0.18em bei 11 px rund
2.0 px und 0.14em bei 10 px rund 1.4 px.

**Drittens, neu in 5.0: statische Schnitte, keine variablen.** Die
drei Familien des Entwurfs gibt es bei Google Fonts als *variable*
Schriftdateien - eine Datei, in der das Gewicht eine stufenlose Achse
ist. Qt meldet sie klaglos an, `QFont.setWeight()` bewegt die Achse
aber nicht: Regular, SemiBold und Bold sehen danach identisch aus,
und was nach Fettung aussieht, hat Qt selbst dazugerechnet. Genau die
Art stiller Fehler, gegen die dieses Modul geschrieben wurde - nur
eine Ebene tiefer.

Beigelegt sind deshalb **festgenagelte Schnitte** (mit
`fonttools varLib.instancer` aus den variablen Dateien erzeugt, opsz
bei Newsreader auf 24). Wer eine Fassung nachziehen will, erzeugt sie
auf demselben Weg neu; die Lizenzdateien liegen daneben.
"""

from __future__ import annotations

from PySide6.QtGui import QFont, QFontDatabase

from core.resources import Resources

from gui.theme import tokens


#
# Die beigelegten Schnitte. Mehr Gewichte braucht der Entwurf nicht:
# er kennt 400, 600 und 700 fuer Inter sowie 400 und 700 fuer die
# Monospace. Was fehlt, synthetisiert Qt - was hier steht, ist echt
# gezeichnet.
#

FONT_FILES = (

    #
    # Display: Ueberschriften und einzelne grosse Saetze. Die Kursive
    # traegt im Entwurf Bedeutung (der Nachsatz einer Zeile) und ist
    # deshalb echt gezeichnet und nicht schraeggestellt.
    #

    "assets/fonts/Newsreader-Regular.ttf",
    "assets/fonts/Newsreader-Medium.ttf",
    "assets/fonts/Newsreader-SemiBold.ttf",
    "assets/fonts/Newsreader-Italic.ttf",
    "assets/fonts/Newsreader-MediumItalic.ttf",

    #
    # Alles Bedienbare. Vier Gewichte, weil der Entwurf 400 (Fliess),
    # 500 (Beschriftung), 600 (Karte, Knopf) und 700 unterscheidet.
    #

    "assets/fonts/IBMPlexSans-Regular.ttf",
    "assets/fonts/IBMPlexSans-Medium.ttf",
    "assets/fonts/IBMPlexSans-SemiBold.ttf",
    "assets/fonts/IBMPlexSans-Bold.ttf",

    #
    # Zahlen, Zeiten, Versionen und die gesperrten Rubriklabels.
    #

    "assets/fonts/IBMPlexMono-Regular.ttf",
    "assets/fonts/IBMPlexMono-Medium.ttf",
    "assets/fonts/IBMPlexMono-SemiBold.ttf",

)


_installed: list[str] = []

_install_done = False


def install_fonts() -> list[str]:
    """
    Die beigelegten Schriften bei Qt anmelden.

    Einmal beim Programmstart, **vor** dem ersten `setStyleSheet` -
    danach angemeldete Familien wirken sich auf bereits gestaltete
    Widgets nicht mehr aus.

    Ein Fehlschlag ist kein Grund abzubrechen: die Anwendung bleibt mit
    einer Systemschrift bedienbar. Er wird aber gemeldet, denn genau
    dieses stille Ausweichen war der Fehler, den dieses Modul behebt.
    """

    global _install_done

    if _install_done:
        return list(_installed)

    _install_done = True

    for relative in FONT_FILES:

        path = Resources.path(relative)

        font_id = QFontDatabase.addApplicationFont(path)

        if font_id < 0:

            print(
                f"[WeintCompanion] Schrift konnte nicht geladen werden: "
                f"{relative} - es wird eine Systemschrift verwendet."
            )

            continue

        for family in QFontDatabase.applicationFontFamilies(font_id):

            if family not in _installed:
                _installed.append(family)

    return list(_installed)


def installed_families() -> list[str]:
    """
    Die tatsaechlich angemeldeten Familien - fuer die Diagnose in den
    Einstellungen und fuer Tests.
    """

    return list(_installed)


def is_available(family: str) -> bool:
    """
    Ob eine Familie wirklich vorhanden ist.

    Nicht `QFont(family).family()` fragen: Qt liefert dort den
    gewuenschten Namen zurueck, auch wenn es ihn gar nicht aufloesen
    konnte. Genau diese Hoeflichkeit hat den Fehler bis 1.7 verdeckt.
    """

    return family in QFontDatabase.families()


# ==========================================================
# Schriften aus Tokens
# ==========================================================

def font(name: str, theme=None) -> QFont:
    """
    Die QFont zu einem Typo-Token ("title", "mono", "eyebrow", ...).

    Die Groesse folgt der eingestellten Dichte; die Laufweite wird hier
    gesetzt, weil das Stylesheet sie nicht kann.
    """

    token = tokens.TYPE.get(name)

    if token is None:
        token = tokens.TYPE["body"]

    if theme is None:

        from gui.theme.theme_manager import theme as current_theme

        theme = current_theme()

    size = theme.font_size(token.size)

    result = QFont(token.family)

    #
    # setPixelSize, nicht der Groessenparameter des Konstruktors: der
    # setzt **Punkte**. Der ganze Entwurf ist in Pixeln bemasst, und
    # das Stylesheet setzt `font-size: Npx` - eine ueber QFont gesetzte
    # Punktgroesse waere bei 96 dpi rund ein Drittel groesser als
    # dieselbe Zahl im Stylesheet. Die Rubriklabels stuenden dann neben
    # ihrem eigenen Abschnittstitel in der falschen Groesse.
    #

    result.setPixelSize(size)

    result.setWeight(QFont.Weight(token.weight))

    if token.italic:
        result.setItalic(True)

    if token.letter_spacing:

        #
        # em -> px. Negative Werte (type.title sperrt enger, -0.02em)
        # funktionieren hier genauso.
        #

        result.setLetterSpacing(
            QFont.AbsoluteSpacing,
            token.letter_spacing * size,
        )

    if token.uppercase:

        result.setCapitalization(QFont.AllUppercase)

    return result


def apply_font(widget, name: str, theme=None):
    """
    Ein Typo-Token auf ein Widget anwenden.

    Bequemlichkeit fuer den haeufigsten Fall - und die Stelle, an der
    sichtbar bleibt, dass Schriftrollen ueber `setFont` und nicht ueber
    das Stylesheet gesetzt werden, sobald eine Laufweite im Spiel ist.
    """

    widget.setFont(font(name, theme))

    return widget
