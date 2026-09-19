"""
Warum sich das Addon nicht installieren lässt - in einem Satz, der den
nächsten Schritt nennt.

Gemeldet wurde: „Update lässt sich nicht installieren, bei *Jetzt
aktualisieren* startet der Download normal, bricht dann aber einfach
wieder ab." Im Protokoll stand

    Installation fehlgeschlagen: [WinError 5] Zugriff verweigert:
    'C:\\Program Files (x86)\\World of Warcraft\\_classic_\\...'

- eine Meldung des Betriebssystems, in der nichts vorkommt, was jemand
daraufhin tun könnte. Zwei völlig verschiedene Ursachen erzeugen sie:

1. **Der Ordner gehört dem System.** Liegt WoW unter `Program Files`,
   darf ein gewöhnlich gestartetes Programm dort nicht schreiben. Dann
   scheitert schon das Anlegen der neuen Fassung.
2. **Der Ordner ist gerade in Benutzung.** Läuft WoW (oder steht der
   Ordner in einem Explorer-Fenster offen), lässt sich der bestehende
   Addon-Ordner unter Windows nicht umbenennen - auch mit allen
   Rechten nicht.

Der Unterschied entscheidet, was zu tun ist: einmal WeintCompanion als
Administrator starten, einmal WoW beenden. Ein gemeinsamer Satz wäre
für einen der beiden Fälle falsch.

**Unterschieden wird über eine Probe, nicht über eine Prozessliste.**
Ob WoW läuft, ließe sich nur mit einer Prozessabfrage beantworten -
plattformabhängig, und auf einer gesperrten Sitzung selbst wieder eine
Rechtefrage. Die Probe beantwortet dieselbe Frage aus der Sache heraus:
lässt sich im Addon-Verzeichnis überhaupt etwas anlegen? Wenn nein,
sind es die Rechte. Wenn ja und trotzdem scheitert das Umbenennen des
bestehenden Ordners, hält ihn jemand offen.

Rein - kein Qt, kein Netz - aus demselben Grund wie `net_errors.py` und
`access_roles.build_profile_payload()`: welcher Satz dort steht, ist die
Stelle, an der etwas falsch sein kann, und die soll ohne laufendes
Programm prüfbar bleiben. Die eine Funktion, die die Platte anfasst
(`probe_writable()`), ist deshalb von der Beurteilung getrennt.
"""

from __future__ import annotations

import errno
import os
import tempfile
from pathlib import Path


class InstallTargetError(RuntimeError):
    """
    Es steht nicht fest, **wohin** installiert werden soll.

    Der Fall liegt noch vor der Rechtefrage: ohne hinterlegten
    WoW-Ordner gibt es kein `Interface/AddOns`, über dessen Rechte
    sich streiten ließe. Er ist bis 5.0.1 gar nicht geprüft worden -
    `state.addon_path` war dann `None`, und `Path(None)` warf

        argument should be a str or an os.PathLike object where
        __fspath__ returns a str, not 'NoneType'

    also die Innereien einer Bibliothek an eine Stelle, an der jemand
    nur wissen will, was er tun soll. `str(exc)` ist hier wie bei
    `InstallPermissionError` der fertige deutsche Satz.
    """


class InstallPermissionError(PermissionError):
    """
    Ein Zugriffsfehler, der seinen Grund und den nächsten Schritt schon
    kennt.

    Erbt von `PermissionError`, damit bestehende `except OSError`-Zweige
    sie weiterhin fangen; `str(exc)` ist der fertige deutsche Satz, den
    Protokoll und Update-Karte anzeigen.
    """


#
# Die Fehlernummern, die "darfst du nicht" heißen. Unter Windows ist
# `WinError 5` als `errno.EACCES` sichtbar; `EPERM` kommt aus derselben
# Ecke und führt zum selben nächsten Schritt.
#

PERMISSION_ERRNOS = (errno.EACCES, errno.EPERM)

#
# Der Rückfall, wenn die Ausnahmekette kein `errno` hergibt. Beide
# Sprachen, weil die Meldung vom Betriebssystem kommt und in dessen
# Sprache steht.
#

PERMISSION_MARKERS = (
    "permission denied",
    "access is denied",
    "zugriff verweigert",
    "winerror 5",
    "winerror 32",
)

#
# Verzeichnisse, in die ein gewöhnlich gestartetes Windows-Programm
# nicht schreiben darf. Klein geschrieben verglichen: Windows-Pfade
# sind nicht schreibungsempfindlich, und der Nutzer kann die Ordner
# auf einem anderen Laufwerk haben.
#

PROTECTED_MARKERS = (
    "program files",
    "programme",
    "windows\\system32",
)


def _chain(exc):
    """
    Die Ausnahme und alles, was sie ausgelöst hat.
    """

    seen = set()

    while exc is not None and id(exc) not in seen:

        seen.add(id(exc))

        yield exc

        exc = exc.__cause__ or exc.__context__


def is_permission_error(exc) -> bool:
    """
    Ist das ein "darfst du nicht"?

    Geprüft wird über `errno` und den Text, nicht über einen
    `isinstance`-Test: `shutil.copytree` verpackt seine Fehler in
    `shutil.Error`, und `zipfile` reicht `OSError` durch - dieselbe
    Ursache erreicht uns also unter mehreren Klassen.
    """

    for item in _chain(exc):

        if isinstance(item, PermissionError):
            return True

        number = getattr(item, "errno", None)

        if number in PERMISSION_ERRNOS:
            return True

        text = str(item).lower()

        if any(marker in text for marker in PERMISSION_MARKERS):
            return True

    return False


def in_protected_location(path) -> bool:
    """
    Liegt der Pfad in einem Verzeichnis, das dem System gehört?

    Nur ein Hinweis für den Satz, nie eine Bedingung: wer WoW nach
    `D:\\Spiele` gelegt und dort die Rechte verstellt hat, bekommt
    denselben Fehler ohne dieses Merkmal - und braucht dieselbe Hilfe.
    """

    text = str(path).replace("/", "\\").lower()

    return any(marker in text for marker in PROTECTED_MARKERS)


def probe_writable(path) -> bool:
    """
    Lässt sich in diesem Verzeichnis etwas anlegen?

    Der nächste vorhandene Ordner oberhalb wird geprüft, denn bei einer
    Neuinstallation gibt es `Interface/AddOns` womöglich noch gar nicht -
    und angelegt werden müsste er dann ebenfalls dort, wo die Rechte
    fehlen.

    Gibt `True` zurück, wenn die Frage nicht zu beantworten ist: eine
    Probe, die im Zweifel blockiert, hielte jemanden von einer
    Installation ab, die funktioniert hätte.
    """

    folder = Path(path)

    while True:

        if folder.is_dir():
            break

        parent = folder.parent

        if parent == folder:
            return True

        folder = parent

    try:

        handle, name = tempfile.mkstemp(
            prefix=".weintcodex-probe-", dir=folder
        )

    except PermissionError:
        return False

    except OSError as exc:

        if exc.errno in PERMISSION_ERRNOS:
            return False

        #
        # Volle Platte, zu langer Pfad, Netzlaufwerk weg: alles echte
        # Probleme, aber keine Rechtefrage. Sie melden sich beim
        # eigentlichen Kopieren mit ihrer eigenen Meldung.
        #

        return True

    os.close(handle)

    try:
        os.unlink(name)
    except OSError:
        pass

    return True


def missing_target_message() -> str:
    """
    Der Satz für "es ist gar kein Spielordner hinterlegt".

    Er nennt den Ort, an dem die Frage beantwortet wird, und nicht die
    fehlende Variable: dass intern `addon_path` leer ist, hilft
    niemandem weiter - dass unter "Einstellungen → WoW-Client" ein
    Ordner fehlt, schon.

    Für Forever ist das **kein Randfall**: die Spielversion ist noch
    nicht erschienen, der Ordnername in `core/wow_clients.py` ist eine
    Vermutung, und die Kennzeichensuche findet nichts, solange nichts
    installiert ist. Wer die App vor dem Spiel einrichtet, landet
    genau hier.
    """

    return (
        "Es ist kein World-of-Warcraft-Ordner hinterlegt - damit steht "
        "nicht fest, wohin WeintCodex installiert werden soll. Wähle "
        "deine Installation unter „Einstellungen → WoW-Client“ aus "
        "(dort liegt auch die Suche) und starte die Installation "
        "danach erneut."
    )


def permission_message(path, *, folder_writable: bool) -> str:
    """
    Der Satz für den Nutzer.

    `folder_writable` ist die Antwort von `probe_writable()` auf das
    Addon-Verzeichnis und entscheidet, welche der beiden Ursachen
    genannt wird.
    """

    where = f"„{path}“" if path else "der Addon-Ordner"

    if folder_writable:

        return (
            "Der bestehende Addon-Ordner lässt sich nicht ersetzen - "
            f"etwas hält ihn gerade offen ({where}). Beende World of "
            "Warcraft, schließe ein Explorer-Fenster auf diesem Ordner "
            "und starte das Update erneut. Deine Einstellungen und "
            "Notizen sind unberührt; ein Backup wurde vorher angelegt."
        )

    if in_protected_location(path):

        return (
            f"Kein Schreibrecht auf {where}. World of Warcraft liegt "
            "unter „Program Files“, und dort darf ein normal "
            "gestartetes Programm nichts ändern. Starte WeintCompanion "
            "einmal als Administrator (Rechtsklick auf die Verknüpfung "
            "→ „Als Administrator ausführen“) und aktualisiere erneut."
        )

    return (
        f"Kein Schreibrecht auf {where}. Starte WeintCompanion einmal "
        "als Administrator, oder gib deinem Benutzerkonto Schreibrechte "
        "auf den WoW-Ordner - danach läuft das Update wie gewohnt."
    )


def translate(exc, path, *, folder_writable: bool):
    """
    Aus einer Ausnahme die Ausnahme mit dem besseren Satz machen.

    Ist es keine Rechtefrage, kommt die ursprüngliche Ausnahme
    unverändert zurück: ein erfundener Rat zu einem Fehler, den wir
    nicht verstanden haben, ist schlechter als die rohe Meldung.
    """

    if isinstance(exc, InstallPermissionError):
        return exc

    if not is_permission_error(exc):
        return exc

    return InstallPermissionError(
        permission_message(path, folder_writable=folder_writable)
    )
