"""
Welche Spielversion diese App bedient.

Seit 5.0 gibt es nur noch eine: *World of Warcraft: Forever*. Die
Tabelle unten hat deshalb genau einen Eintrag - und bleibt trotzdem
eine Tabelle.

WARUM EINE TABELLE MIT EINEM EINTRAG
------------------------------------

Weil der Fehler, den sie verhindert, unabhängig von ihrer Länge ist.
Bis 4.0 hiess "WoW" stillschweigend Mists of Pandaria, und der
Ordnername `_classic_` stand an sechs Stellen im Quelltext - in der
Ordnerprüfung, in der Suche, in der Konfiguration, in drei
Beschriftungen. Eine Spielversion war kein Gegenstand, sondern eine
Annahme, und als eine zweite dazukam, war der Umbau grösser als die
Änderung.

Forever ist zum Zeitpunkt dieses Eintrags **noch nicht erschienen**
(4. November 2026). Es wird also mindestens noch einen Zeitpunkt
geben, an dem sich hier etwas ändert: wenn der Ordnername feststeht.
Dass das eine Zeile ist und kein Umbau, ist der ganze Zweck dieser
Datei.

WAS ÜBER FOREVER NOCH NICHT BEKANNT IST
---------------------------------------

**Der Ordnername.** Blizzard nennt die Unterordner unter
"World of Warcraft" seit jeher `_retail_`, `_classic_`,
`_classic_era_`. `_forever_` unten ist die naheliegende Fortsetzung
dieser Reihe und damit eine **Vermutung**, keine Auskunft - im
Betatest wurde `_classic_beta_` beobachtet, also der Ordner, den
Blizzard für jede Classic-Beta verwendet. Deshalb gilt weiterhin:

- Ein *bekannter* Ordnername wird direkt unter der gewählten Wurzel
  gesucht.
- Trifft er nicht zu, entscheiden allein die Kennzeichen einer
  Installation (`Interface/AddOns`, `WTF`), und fremde Spielversionen
  werden über `FOREIGN_FLAVOR_FOLDERS` ausgeschlossen.

Die Suche steht und fällt deshalb **nicht** mit der Vermutung. Stimmt
sie, geht es einen Schritt schneller; stimmt sie nicht, findet die
Kennzeichensuche die Installation trotzdem.

**Die Höchststufe** ist dagegen bekannt und bestätigt: Forever bleibt
bei **60**. Damit ist `max_level=None` ("noch unbekannt") für diese
Version Vergangenheit - der Fall bleibt im Datentyp erhalten, weil er
für jede künftige Version wieder eintreten wird, und weil
`core/character_store.default_min_level()` ihn bereits richtig
behandelt: aus einer Datenlücke wird kein Befund.

WAS HIER NICHT HINEINGEHÖRT
---------------------------

Alles, was die *Auswertung* betrifft: Encounter-Tabellen
(`analyzer/data/encounters.py`), Spezialisierungen
(`analyzer/data/specs.py`). Die hängen an der Spielversion, aber nicht
an ihrem *Installationsort*. Diese Datei beantwortet ausschliesslich:
**welche Version, und wo liegt sie.**
"""

from __future__ import annotations

from dataclasses import dataclass, field


#
# Die drei Kennzeichen einer WoW-Installation, an denen sie sich seit
# der ersten Fassung erkennen lässt. Sie stehen hier als Vorgabe und
# nicht fest verdrahtet in der Prüfung, damit eine Spielversion sie
# überschreiben kann, falls Forever den Aufbau doch ändert.
#

STANDARD_MARKERS: tuple[tuple[str, ...], ...] = (

    ("Interface",),
    ("Interface", "AddOns"),
    ("WTF",),

)


@dataclass(frozen=True)
class WowClient:
    """
    Eine Spielversion und das, was diese App über sie wissen muss.
    """

    id: str

    #
    # Der volle Name für Überschriften und Dateidialoge, die Kurzform
    # für Statuszeilen ("Forever · _forever_").
    #

    name: str

    short_name: str

    #
    # Die möglichen Namen des Installationsordners unter der
    # Battle.net-Wurzel. **Leer heisst "noch unbekannt"**, nicht
    # "keiner" - siehe Modulkommentar.
    #

    folder_names: tuple[str, ...] = ()

    #
    # Höchststufe, oder None solange unbekannt.
    #

    max_level: int | None = None

    #
    # Erschienen? Eine nicht erschienene Version lässt sich bereits
    # einrichten - der Ordner wird dann von Hand gewählt, weil es
    # nichts zu finden gibt.
    #

    released: bool = True

    #
    # Einzeiler unter der Auswahl. Trägt, was der Nutzer über diese
    # Version wissen muss.
    #

    hint: str = ""

    markers: tuple[tuple[str, ...], ...] = field(
        default=STANDARD_MARKERS,
    )

    # --------------------------------------------------

    @property
    def folder_known(self) -> bool:
        """
        Ist der Name des Installationsordners bekannt?
        """

        return bool(self.folder_names)


# --------------------------------------------------
# Die Tabelle
# --------------------------------------------------


FOREVER = WowClient(

    id="forever",

    name="World of Warcraft: Forever",

    short_name="Forever",

    #
    # Vermutung, kein Wissen - siehe Modulkommentar. Sie darf hier
    # stehen, weil ein Fehlgriff folgenlos ist: findet sich der Ordner
    # nicht, sucht `core/wow_folder.py` über die Kennzeichen weiter.
    #

    folder_names=("_forever_",),

    #
    # Bestätigt: Forever bleibt bei Stufe 60.
    #

    max_level=60,

    #
    # Erscheint am 4. November 2026. Bis dahin gibt es nichts zu
    # finden; die Einrichtung sagt das und lässt den Ordner von Hand
    # wählen, statt eine Suche anzubieten, die nur leer ausgehen kann.
    #

    released=False,

    hint=(
        "Forever erscheint am 4. November 2026. Solange es nicht "
        "installiert ist, gibt es keinen Ordner zu finden - danach "
        "sucht die App ihn von selbst."
    ),

)


CLIENTS: tuple[WowClient, ...] = (

    FOREVER,

)


DEFAULT_CLIENT_ID = FOREVER.id


#
# Alle Unterordnernamen, die Blizzard für *andere* Spielversionen
# vergibt - einschliesslich Testumgebungen. Sie sind der Unterschied
# zwischen "irgendeine Installation" und "die gesuchte": ohne sie
# würde eine Suche im Zweifel `_retail_` finden und als Forever
# ausgeben.
#
# `_classic_beta_` steht bewusst hier und **nicht** bei
# `folder_names`, obwohl die Forever-Beta darin lief: denselben Ordner
# benutzt Blizzard für jede Classic-Beta, und eine liegengebliebene
# Installation daraus als Forever auszugeben wäre genau die stille
# Verwechslung, gegen die diese Liste da ist. Wer die Beta bedienen
# will, wählt ihren Ordner von Hand.
#

FOREIGN_FLAVOR_FOLDERS: tuple[str, ...] = (

    "_retail_",
    "_classic_",
    "_classic_era_",
    "_ptr_",
    "_xptr_",
    "_beta_",
    "_classic_ptr_",
    "_classic_beta_",
    "_classic_era_ptr_",

)


# --------------------------------------------------
# Zugriff
# --------------------------------------------------


def all_clients() -> tuple[WowClient, ...]:

    return CLIENTS


def client(client_id) -> WowClient:
    """
    Die Spielversion zu einer Kennung.

    **Eine unbekannte Kennung fällt auf die Vorgabe zurück und wirft
    nicht.** Der Wert kommt aus der `config.json` und damit aus einer
    Datei, die ein Nutzer von Hand ändern kann; eine Ausnahme beim
    Start wäre die härteste denkbare Antwort auf einen Tippfehler.

    Seit 5.0 hat das einen zweiten Zweck: in der Konfiguration eines
    Nutzers, der von der alten Companion herüberkommt, steht noch
    `mop_classic`. Auch die fällt hier auf Forever zurück - still und
    ohne Fehler, denn eine Spielversion, die es in dieser App nicht
    mehr gibt, ist kein Fehler des Nutzers.
    """

    for candidate in CLIENTS:

        if candidate.id == client_id:
            return candidate

    return default_client()


def default_client() -> WowClient:

    for candidate in CLIENTS:

        if candidate.id == DEFAULT_CLIENT_ID:
            return candidate

    return CLIENTS[0]


def released_clients() -> tuple[WowClient, ...]:
    """
    Die Spielversionen, die es tatsächlich schon gibt.

    Die Einrichtung fragt nur dann nach der Version, wenn es hier mehr
    als eine gibt. Solange Forever nicht erschienen ist, ist diese
    Antwort **leer** - und die Einrichtung behandelt das wie den Fall
    "eine einzige": sie fragt nicht, sondern nimmt die Vorgabe. Eine
    Auswahl zwischen null Möglichkeiten ist keine Frage.
    """

    return tuple(
        candidate
        for candidate in CLIENTS
        if candidate.released
    )


def foreign_flavor_folders(target: WowClient) -> tuple[str, ...]:
    """
    Die Ordnernamen anderer Spielversionen - also alle bekannten ausser
    denen der übergebenen.
    """

    own = set(target.folder_names)

    return tuple(
        name
        for name in FOREIGN_FLAVOR_FOLDERS
        if name not in own
    )
