VERSION = "1.2.0"


def parse_version(value):
    """
    Zerlegt eine Versionsangabe in ein Zahlen-Tupel, fehlende Teile
    werden mit 0 aufgefüllt - "0.8" und "0.8.0" ergeben so denselben
    Wert (0, 8, 0). Ohne das würden GitHub-Tags wie "v0.8" (statt
    "v0.8.0") beim reinen String-Vergleich als andere Version gelten
    und fälschlich ein "Update verfügbar" bzw. "Changelog nicht
    gefunden" auslösen.
    """

    value = (
        (value or "")
        .strip()
        .lower()
        .removeprefix("v")
    )

    numbers = []

    for part in value.split("."):

        digits = ""

        for char in part:

            if char.isdigit():
                digits += char
            else:
                break

        numbers.append(
            int(digits) if digits else 0
        )

    while len(numbers) < 3:
        numbers.append(0)

    return tuple(numbers)


def versions_equal(a, b):

    return parse_version(a) == parse_version(b)


#
# Die Umstellung auf Forever (1.0.0): Companion und Addon zählen neu ab
# 1.0 (vorher 5.5.0 und 6.146.0.0). Ein Update gilt weiter, sobald die
# Fassungen *verschieden* sind (`versions_equal`), nicht erst, wenn die
# neue höher ist - deshalb sehen bestehende Installationen 1.0.0 trotz
# der kleineren Zahl. Ist die angebotene Fassung kleiner als die
# installierte, ist es genau diese Umstellung, und der Knopf sagt das,
# statt "aktualisieren" auf eine kleinere Zahl zu schreiben. Danach
# laufen Updates wieder aufwärts, und der Knopf heisst wie immer.
#

SWITCH_LABEL = "Umstellung auf Forever"


def is_forever_switch(installed, latest) -> bool:

    if not installed or not latest or str(installed).strip() in ("-", ""):
        return False

    return parse_version(latest) < parse_version(installed)


def update_label(installed, latest, default: str) -> str:

    return SWITCH_LABEL if is_forever_switch(installed, latest) else default
