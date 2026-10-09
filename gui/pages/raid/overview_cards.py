"""
Die Raid-Karten der Übersicht - ruhend seit 5.1 (Forever).

Bis 5.0 standen hier auf der Übersicht die Aufstellung des nächsten
Raids (`RosterCard`) und der letzte Pull (`LastPullCard`). Auf Forever
gibt es noch keinen Raid; die Karten sind deshalb aus der Übersicht
genommen, aber nicht gelöscht: sie liegen hier neben dem ruhenden Raid
Center und bleiben unter Test (`tests/test_roster_card.py`,
`tests/test_last_pull_card.py`). Zurück auf die Übersicht kommen sie
zusammen mit `RAID_FEATURES` in `core/companion_manager.py` - siehe
`docs/systems/raid-center.md`, Abschnitt *Ruht seit 5.1*.

Die Kommentare unten sind die von 5.0 und beschreiben die Karten so,
wie sie auf der Übersicht standen.
"""

from __future__ import annotations


from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


from core.last_pull import (
    LastPull,
    result_text,
    when_text,
)
from core.raid_schedule import (
    ROLE_LABELS,
    ROLE_ORDER,
    composition_text,
    count_text,
    day_text,
    open_slots,
    others_text,
    own_signup_label,
    own_signup_text,
    own_signup_variant,
    signup_text,
)
from gui.navigation import (
    RAID_VIEW_ANALYSIS,
    RAID_VIEW_LEARN,
    RaidLink,
)
from gui.theme import tokens
from gui.theme.fonts import font
from gui.theme.restyle import restyle
from gui.theme.theme_manager import theme
from gui.widgets.card import Card
from gui.widgets.chip import Chip
from gui.widgets.eyebrow import eyebrow_label
from gui.widgets.sparkline import Sparkline
from gui.widgets.roster_strip import RosterStrip, SlotGroup
from gui.widgets.academy.star_rating import Rating
from gui.widgets.wrapped_label import enable_wrap


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


def _slot_groups(schedule, day) -> list[SlotGroup]:
    """
    Die Reihen des Aufstellungsstreifens.

    Drei Fälle, und sie unterscheiden sich in dem, was der Bot
    geliefert hat - nicht in dem, was die Karte gerne hätte:

    - **Rollen gemeldet**: eine Reihe je Rolle, gefüllt mit den
      Klassen der Zusagen, dahinter die fehlenden Plätze dieser Rolle
      (nur wenn eine Sollstärke gemeldet ist). Was danach noch offen
      ist, steht als eigene Reihe "FREI" - die Sollstärke sagt, wie
      viele Heiler gebraucht werden, nicht, wie der letzte Platz zu
      besetzen ist.
    - **Nur Zahlen**: ein einziger Streifen "ZUGESAGT". Drei Reihen
      aus einer Gesamtzahl zu schätzen wäre in der Anzeige von einer
      gemeldeten Aufstellung nicht zu unterscheiden.
    - **Keine Raidgröße und keine Zusage**: gar kein Streifen. Ein
      leerer Rahmen ohne einen einzigen Platz ist kein Bild, sondern
      ein Ladefehler.
    """

    if day is None:
        return []

    size = int(getattr(schedule, "raid_size", 0) or 0)

    total_open, missing, free = open_slots(schedule, day)

    if day.has_roles():

        groups = []

        for role in ROLE_ORDER:

            filled = [
                slot.class_name
                for slot in day.roster
                if slot.role == role
            ]

            gap = missing.get(role, 0)

            if not filled and not gap:
                continue

            groups.append(
                SlotGroup(
                    label=ROLE_LABELS[role],
                    filled=filled,
                    open_slots=gap,
                )
            )

        if free:

            groups.append(SlotGroup(label="FREI", open_slots=free))

        return groups

    if not day.active and not size:
        return []

    #
    # Ohne Rollen: ein Streifen. Die gefüllten Plätze tragen keine
    # Klasse und erscheinen deshalb in Akzentfarbe.
    #

    return [
        SlotGroup(
            label="ZUGESAGT",
            filled=[""] * day.active,
            open_slots=total_open,
        )
    ]


class DayBlock(QWidget):
    """
    Ein Termin des Raids: Zeile, Zahl, Streifen, Satz.

    **Warum es diesen Block gibt.** Der Standardraid laeuft Mittwoch
    *und* Donnerstag, und die beiden Anmeldungen sind zwei verschiedene
    Listen - wer am Mittwoch zusagt, muss am Donnerstag nicht koennen.
    Die Karte nannte aber nur den naechsten Termin: am Dienstag also
    den Mittwoch, waehrend der Donnerstag daneben leer sein konnte,
    ohne dass es in der App zu sehen war. Der Bot schickt beide Tage in
    derselben Antwort, sie standen nur nie auf dem Bildschirm.

    Die Zahl sitzt in der Zeile ueber *ihrem* Streifen und nicht mehr
    im Kopf der Karte: mit zwei Tagen gehoert "21 / 25" zu einem von
    beiden, und im Kopf waere nicht zu sehen, zu welchem.

    Aus demselben Grund steht auch die **eigene Anmeldung** hier und
    nicht im Kopf: der Chip neben dem Datum sagt, ob man selbst fuer
    diesen Tag zugesagt, abgesagt oder noch gar nicht geantwortet hat.
    "21 von 25 zugesagt" beantwortet diese Frage nicht - die Antwort
    des Bots nennt bewusst keine Namen, es ist aus ihr also gar nicht
    zu erkennen, wer von den 21 man selbst ist. Sie kommt deshalb als
    eigenes Feld je Tag (`days[].me`, siehe `core/raid_schedule.py`).
    """

    def __init__(self, parent=None):

        super().__init__(parent)

        root = QVBoxLayout(self)

        root.setContentsMargins(0, 0, 0, 0)

        root.setSpacing(4)

        head = QHBoxLayout()

        head.setContentsMargins(0, 0, 0, 0)

        head.setSpacing(tokens.SPACE[1])

        self.when = QLabel("")

        self.when.setFont(font("body"))

        restyle(
            self.when,
            f"color:{tokens.TEXT['primary']};background:transparent;",
        )

        head.addWidget(self.when)

        #
        # Der eigene Anmeldezustand, direkt neben dem Datum: er
        # gehört zu **diesem** Tag und nicht zum Raid. Mittwoch und
        # Donnerstag sind zwei Anmeldungen, und ein Hinweis im Kopf
        # der Karte müsste offenlassen, welchen der beiden er meint -
        # dieselbe Überlegung, die die Zahl der Zusagen aus dem Kopf
        # in die Tageszeile geholt hat.
        #
        # Unsichtbar, solange der Bot nichts dazu meldet: kein Chip
        # heisst "dazu ist nichts bekannt", und das ist etwas anderes
        # als "nicht angemeldet".
        #

        self.own = Chip("", "neutral")

        self.own.setVisible(False)

        head.addWidget(self.own)

        head.addStretch(1)

        self.count = QLabel("")

        self.count.setFont(font("small"))

        restyle(
            self.count,
            f"color:{tokens.TEXT['secondary']};background:transparent;",
        )

        head.addWidget(self.count)

        root.addLayout(head)

        self.strip = RosterStrip()

        self.strip.setVisible(False)

        root.addSpacing(tokens.SPACE[0])

        root.addWidget(self.strip)

        self.note = QLabel("")

        self.note.setFont(font("small"))

        enable_wrap(self.note)

        restyle(
            self.note,
            f"color:{tokens.TEXT['secondary']};background:transparent;",
        )

        root.addWidget(self.note)

    # --------------------------------------------------

    def apply(self, schedule, day):

        self.when.setText(day_text(day))

        label = own_signup_label(day)

        self.own.setText(label)

        self.own.setVariant(own_signup_variant(day))

        #
        # Der ganze Satz hängt am Chip: "NICHT ANGEMELDET" ist die
        # kurze Fassung, "Deine Anmeldung für diesen Tag fehlt noch."
        # die, in der die Frage gestellt wird.
        #

        self.own.setToolTip(own_signup_text(day))

        self.own.setVisible(bool(label))

        self.count.setText(count_text(day, schedule.raid_size))

        groups = _slot_groups(schedule, day)

        self.strip.setGroups(groups)

        self.strip.setVisible(bool(groups))

        text = _day_note(schedule, day, bool(groups))

        self.note.setText(text)

        self.note.setVisible(bool(text))


def _day_note(schedule, day, has_strip: bool) -> str:
    """
    Der Satz unter einem Streifen.

    Mit Streifen sagt er, **was** fehlt (die Zahl steht schon in der
    Zeile darueber); ohne Streifen bleibt es bei der alten Zeile mit
    der Zahl, sonst stuende unter dem Termin gar nichts. "Vielleicht"
    und "Ersatzbank" haengen in beiden Faellen hinten dran - sie
    gehoeren neben die Zusagen, nicht hinein.

    Dass die Anmeldung geschlossen ist, steht hier **nicht**: das gilt
    fuer den Raid und nicht fuer einen seiner Tage, und zweimal
    untereinander gelesen sieht es aus wie zwei verschiedene Auskuenfte.
    Es steht im Kopf der Karte.
    """

    parts = []

    if has_strip:

        parts.append(composition_text(schedule, day))

        if day.tentative:
            parts.append(f"{day.tentative} vielleicht")

        if day.bench:
            parts.append(f"{day.bench} Ersatzbank")

    else:

        parts.append(signup_text(day, schedule.raid_size))

    return " · ".join(part for part in parts if part)


class RosterCard(Card):
    """
    Der nächste Raid: Termin, Titel, **Aufstellung**.

    **Was sich hier geändert hat.** Bis 2.0.1 stand an dieser Stelle
    "Zusagen und Rollen sind der App nicht bekannt", und das stimmte:
    der Roster erreicht die Companion als zwei undurchsichtige
    WCIMPORT-Zeichenketten (`core/discord_roster_sync.py`), die
    ungeparst ans Addon weitergehen - und die bekommt ohnehin nur, wer
    die Raidlead-Rolle trägt.

    Der Bot beantwortet die Frage jetzt eigens
    (`/companion/raid-schedule`, für jeden verknüpften Nutzer). Seit
    2.0.7 steht hier die Aufstellung so, wie sie im Entwurf der
    Übersicht stand: je Rolle eine Reihe Plätze, gefüllte in
    Klassenfarbe, offene als Lücke, darunter ein Satz, was noch fehlt.
    "10 von 25" ist die Zahl; die Frage vor einem Raid ist aber, *wer*
    fehlt - vier offene Plätze sind harmlos, wenn es Schaden ist, und
    ein Abend ohne Raid, wenn es der zweite Tank ist.

    Was weiterhin **nicht** hier steht, ist die Namensliste: der
    Endpunkt liefert Rolle und Klasse, niemals einen Namen. Beides
    steht als Symbol im Anmelde-Beitrag, den jeder im Kanal lesen
    kann; die Namen bleiben hinter der Raidlead-Rolle. Wer sie sehen
    will, geht über den Knopf ins Discord.

    Seit 2.3.4 zeigt sie **jeden noch bevorstehenden Termin**, nicht
    nur den naechsten: der Standardraid laeuft Mittwoch und
    Donnerstag, und das sind zwei Anmeldungen - wer am Mittwoch zusagt,
    muss am Donnerstag nicht koennen. Der Bot schickte beide Tage von
    Anfang an in derselben Antwort; hier stand nur einer davon, und ob
    der zweite ueberhaupt Leute hatte, war in der App nicht zu sehen.
    Jeder Tag ist ein `DayBlock` mit eigener Zahl, eigenem Streifen und
    eigenem Satz.

    Ohne Antwort bleibt die alte Haltung unverändert: die Karte sagt,
    dass nichts bekannt ist, statt "0 von 25" zu behaupten. Eine Null
    wäre keine Untertreibung, sondern eine falsche Messung - niemand
    hat gezählt. Und meldet der Bot den Termin, aber keine Rollen
    (ältere Fassung), steht dort ein einziger Streifen "zugesagt"
    statt drei geschätzter.
    """

    def __init__(self, parent=None):

        super().__init__(parent=parent)

        self.setMinimumHeight(170)

        header = QHBoxLayout()

        header.setContentsMargins(0, 0, 0, 0)

        header.setSpacing(tokens.SPACE[1])

        header.addWidget(eyebrow_label("AUFSTELLUNG"))

        header.addStretch(1)

        #
        # Rechts im Kopf steht, was fuer den **Raid** gilt und nicht
        # fuer einen seiner Tage: dass die Anmeldung geschlossen ist.
        # Die Zahl der Zusagen sass hier, solange die Karte einen
        # einzigen Termin zeigte; mit Mittwoch und Donnerstag
        # untereinander gehoert sie in die Zeile ihres Tages, sonst
        # ist nicht zu sehen, welchen von beiden sie meint.
        #

        self.status = QLabel("")

        self.status.setFont(font("small"))

        restyle(
            self.status,
            f"color:{tokens.TEXT['secondary']};background:transparent;",
        )

        self.status.setVisible(False)

        header.addWidget(self.status)

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

        restyle(
            self.title,
            f"color:{tokens.WHITE};background:transparent;",
        )

        self.title.setVisible(False)

        text.addWidget(self.title)

        #
        # Je Termin ein Block. Sie werden einmal gebaut und danach nur
        # noch beschriftet - dieselbe Regel wie bei den Zeilen unter
        # `gui/widgets/tv/`: ein Neubau bei jedem `refresh()` waere
        # Arbeit fuer ein Bild, das sich meist gar nicht aendert.
        #

        self.days = QVBoxLayout()

        self.days.setContentsMargins(0, 0, 0, 0)

        self.days.setSpacing(tokens.SPACE[3])

        self._blocks: list[DayBlock] = []

        text.addSpacing(tokens.SPACE[1])

        text.addLayout(self.days)

        self.explanation = QLabel(
            "Sobald im Discord ein Termin steht, erscheint er hier - "
            "mit Datum, Uhrzeit und der Aufstellung."
        )

        self.explanation.setFont(font("small"))

        enable_wrap(self.explanation)

        restyle(
            self.explanation,
            f"color:{tokens.TEXT['secondary']};background:transparent;",
        )

        text.addWidget(self.explanation)

        #
        # Die weiteren gleichzeitig laufenden Raids. Eigene Zeile und
        # nicht angehängt an die Erklärung darüber: die spricht über
        # DIESEN Termin (was fehlt, wie viele zugesagt haben), und ein
        # zweiter Raid gehört nicht in denselben Satz. Unsichtbar,
        # solange nur einer läuft - das ist der Normalfall.
        #

        self.parallel = QLabel("")

        self.parallel.setFont(font("small"))

        enable_wrap(self.parallel)

        restyle(
            self.parallel,
            f"color:{tokens.TEXT['muted']};background:transparent;",
        )

        self.parallel.setVisible(False)

        text.addWidget(self.parallel)

        text.addStretch(1)

        body.addLayout(text, 1)

        buttons = QVBoxLayout()

        buttons.setContentsMargins(0, 0, 0, 0)

        buttons.setSpacing(tokens.SPACE[1])

        self.launch = QPushButton("WoW starten")

        self.launch.setCursor(Qt.PointingHandCursor)

        buttons.addWidget(self.launch)

        self.discord = QPushButton("Aufstellung im Discord")

        self.discord.setObjectName("secondary")

        self.discord.setCursor(Qt.PointingHandCursor)

        buttons.addWidget(self.discord)

        buttons.addStretch(1)

        body.addLayout(buttons)

        self.addLayout(body, 1)

    # --------------------------------------------------

    def apply(self, schedule, days):
        """
        `schedule` ist ein `RaidSchedule`, `days` seine noch
        bevorstehenden Termine (`upcoming_days()`), der naechste zuerst.

        Beim Standardraid sind das **zwei**: Mittwoch und Donnerstag
        stehen untereinander, jeder mit seiner eigenen Zahl, seinem
        eigenen Streifen und seinem eigenen Satz. Sie sind zwei
        Anmeldungen und keine zwei Ansichten derselben - eine
        gemeinsame Zahl haette den Donnerstag hinter dem Mittwoch
        verschwinden lassen, und genau darum geht es hier.

        Beides kann leer sein - dann steht wieder da, dass nichts
        bekannt ist. Der Zustand "es gibt einen Raid, aber alle
        Termine liegen hinter uns" ist davon nicht zu trennen und
        bekommt deshalb dieselbe Auskunft.
        """

        days = list(days or [])

        if not getattr(schedule, "known", False) or not days:

            self.title.setVisible(False)

            self._show_days(0)

            self.explanation.setText(
                "Sobald im Discord ein Termin steht, erscheint er "
                "hier - mit Datum, Uhrzeit und der Aufstellung."
            )

            self.explanation.setVisible(True)

            self.status.setVisible(False)

            self.parallel.setVisible(False)

            return

        self.title.setText(schedule.title)

        self.title.setVisible(True)

        for block, day in zip(self._blocks_for(len(days)), days):
            block.apply(schedule, day)

        self._show_days(len(days))

        #
        # Die Erklaerung darunter ist jetzt allein der Platzhalter fuer
        # "nichts bekannt" - was zu einem Termin zu sagen ist, sagt
        # sein eigener Block.
        #

        self.explanation.setVisible(False)

        geschlossen = schedule.signup_status == "locked"

        self.status.setText("Anmeldung geschlossen" if geschlossen else "")

        self.status.setVisible(geschlossen)

        weitere = others_text(schedule)

        self.parallel.setText(weitere)

        self.parallel.setVisible(bool(weitere))

    # --------------------------------------------------

    def _blocks_for(self, count: int) -> list[DayBlock]:
        """
        So viele Bloecke, wie Termine anstehen - fehlende werden
        angelegt, ueberzaehlige bleiben stehen und werden versteckt.

        Weggeworfen wird keiner: ein Raid hat heute zwei Termine, und
        morgen wieder, und ein Widget je Durchgang neu zu bauen kostet
        Layout fuer ein Bild, das gleich bleibt.
        """

        while len(self._blocks) < count:

            block = DayBlock()

            self._blocks.append(block)

            self.days.addWidget(block)

        return self._blocks

    def _show_days(self, count: int):

        for index, block in enumerate(self._blocks):
            block.setVisible(index < count)


class LastPullCard(Card):
    """
    Dein letzter Pull: Ergebnis, schwächster Bereich, eine Lektion.

    **Woher er kommt, und warum das eine Korrektur war.** Bis 2.0.6
    las diese Karte allein `RaidDataService.history()`. Die füllt sich
    aber ausschließlich mit Pulls, die *in dieser Sitzung* endeten,
    während WeintTV oder die Academy offen waren - nach jedem Neustart
    ist sie leer. Am Tag nach einem Raidabend stand hier deshalb "Noch
    kein Pull", und das war keine vorsichtige Auskunft, sondern eine
    falsche: der Kampf hat stattgefunden, die App hat nur an der
    falschen Stelle nachgesehen.

    Seit 2.0.7 ist die Sitzung nur noch die erste von zwei Quellen.
    Findet sich dort nichts, tritt der letzte Pull aus dem
    WarcraftLogs-Archiv an ihre Stelle (`core/last_pull_sync.py`),
    abgeholt im gewöhnlichen Sync-Takt und zwischengespeichert. Die
    Reihenfolge ist Absicht: ein Pull, der gerade eben endete, ist der
    letzte, auch wenn WarcraftLogs ihn noch nicht kennt.

    Was ein Pull aus dem Archiv **nicht** mitbringt, ist die
    Bewertung: dafür müsste der ganze Kampf geladen werden, und das
    kostet den Bot Minuten. Die Sternreihe bleibt dann leer und die
    Lektionskarte sagt, wo die Auswertung zu haben ist - statt einen
    schwächsten Bereich zu nennen, den niemand gemessen hat.
    """

    #
    # Ein Tiefenverweis auf genau diesen Pull. Er trägt die
    # Perspektive mit, weil die beiden Knöpfe zwei verschiedene Fragen
    # stellen: "zeig ihn mir" und "was lerne ich daraus".
    #

    raidCenterRequested = Signal(object)

    def __init__(self, parent=None):

        super().__init__(parent=parent)

        #
        # Der Pull, den die Karte gerade beschreibt. Die Knöpfe lesen
        # ihn beim Klick und nicht beim Bauen: eine Lambda, die den
        # Pull einfängt, wäre beim nächsten `apply()` veraltet.
        #

        self._pull: LastPull | None = None

        header = QHBoxLayout()

        header.setContentsMargins(0, 0, 0, 0)

        header.setSpacing(tokens.SPACE[1])

        header.addWidget(eyebrow_label("DEIN LETZTER PULL"))

        header.addStretch(1)

        self.timestamp = eyebrow_label("", tokens.TEXT["faint"])

        header.addWidget(self.timestamp)

        self.addLayout(header)

        top = QHBoxLayout()

        top.setContentsMargins(0, 0, 0, 0)

        top.setSpacing(tokens.SPACE[3])

        column = QVBoxLayout()

        column.setContentsMargins(0, 0, 0, 0)

        column.setSpacing(2)

        self.boss = QLabel("Noch kein Pull")

        self.boss.setFont(font("section"))

        restyle(
            self.boss,
            f"color:{tokens.WHITE};background:transparent;",
        )

        column.addWidget(self.boss)

        self.result = QLabel(
            "Sobald ein Kampf endet, steht sein Ergebnis hier."
        )

        self.result.setFont(font("small"))

        enable_wrap(self.result)

        restyle(
            self.result,
            f"color:{tokens.TEXT['secondary']};background:transparent;",
        )

        column.addWidget(self.result)

        top.addLayout(column, 1)

        self.sparkline = Sparkline()

        top.addWidget(self.sparkline, alignment=Qt.AlignTop)

        self.addLayout(top)

        self.addWidget(_divider())

        weakest = QHBoxLayout()

        weakest.setContentsMargins(0, 0, 0, 0)

        weakest.setSpacing(tokens.SPACE[1])

        weakest.addWidget(
            eyebrow_label("DEIN FOKUS", tokens.STATE_TEXT["error"])
        )

        self.area = QLabel("—")

        self.area.setFont(font("body"))

        restyle(
            self.area,
            f"color:{tokens.TEXT['primary']};background:transparent;",
        )

        weakest.addWidget(self.area)

        weakest.addStretch(1)

        self.rating = Rating(0)

        weakest.addWidget(self.rating)

        self.addLayout(weakest)

        #
        # Die Lektionskarte: der eine konkrete nächste Schritt. Sie
        # sitzt auf `surface.card` statt auf dem Kartenverlauf, damit
        # sie sich als eigene Ebene absetzt.
        #

        self.lesson = QFrame()

        self.lesson.setObjectName("lessonBox")

        self.lesson.setAttribute(Qt.WA_StyledBackground, True)

        restyle(
            self.lesson,
            f"""
            QFrame#lessonBox{{
                background:{tokens.SURFACE["card"]};
                border:none;
                border-radius:{tokens.RADIUS["md"]}px;
            }}
            """,
        )

        lesson_layout = QVBoxLayout(self.lesson)

        lesson_layout.setContentsMargins(14, 12, 14, 12)

        lesson_layout.setSpacing(6)

        self.lesson_eyebrow = eyebrow_label(
            "EINE LEKTION",
            theme().accent_light(),
        )

        lesson_layout.addWidget(self.lesson_eyebrow)

        self.lesson_title = QLabel("Die Academy schlägt sie vor.")

        self.lesson_title.setFont(font("card"))

        restyle(
            self.lesson_title,
            f"color:{tokens.WHITE};background:transparent;",
        )

        lesson_layout.addWidget(self.lesson_title)

        self.lesson_reason = QLabel(
            "Nach dem ersten ausgewerteten Pull steht hier, woran zu "
            "arbeiten sich am meisten lohnt - mit den Messwerten, aus "
            "denen sich das ergibt."
        )

        self.lesson_reason.setFont(font("small"))

        enable_wrap(self.lesson_reason)

        restyle(
            self.lesson_reason,
            f"color:{tokens.TEXT['secondary']};background:transparent;",
        )

        lesson_layout.addWidget(self.lesson_reason)

        actions = QHBoxLayout()

        actions.setContentsMargins(0, 0, 0, 0)

        actions.setSpacing(tokens.SPACE[1])

        #
        # **Der Hauptweg von hier aus.** Bis 3.6.0 stand hier ein
        # einzelner Knopf "Lektion öffnen", der in die Academy führte -
        # und dort begann die Arbeit von vorn: Charakter wählen, Pull
        # wiederfinden. Jetzt trägt der Verweis den Pull mit, und der
        # erste Knopf ist der, den man zuerst will: **diesen Pull
        # ansehen**.
        #

        self.open_pull = QPushButton("Pull ansehen")

        self.open_pull.setObjectName("secondaryAccent")

        self.open_pull.setCursor(Qt.PointingHandCursor)

        self.open_pull.clicked.connect(self._request_analysis)

        actions.addWidget(self.open_pull)

        self.open_lesson = QPushButton("Daraus lernen")

        self.open_lesson.setObjectName("secondary")

        self.open_lesson.setCursor(Qt.PointingHandCursor)

        self.open_lesson.clicked.connect(self._request_learn)

        actions.addWidget(self.open_lesson)

        actions.addStretch(1)

        lesson_layout.addLayout(actions)

        self.addWidget(self.lesson)

        self.addStretch(1)

    # --------------------------------------------------

    def _request_analysis(self):

        self._request(RAID_VIEW_ANALYSIS)

    def _request_learn(self):

        self._request(RAID_VIEW_LEARN)

    def _request(self, view: str):
        """
        Den Tiefenverweis auf **diesen** Pull ausgeben.

        Bericht und Kampfnummer nur, wenn der Pull sie trägt: ein Pull
        dieser Sitzung hat keine (er lief live mit), und eine halbe
        Kennung würde die bestehende Archivauswahl verwerfen, ohne
        etwas laden zu können.
        """

        pull = self._pull

        self.raidCenterRequested.emit(
            RaidLink(
                view=view,
                report_code=(
                    pull.report_code
                    if pull is not None and pull.report_code and pull.fight_id
                    else ""
                ),
                fight_id=(
                    int(pull.fight_id)
                    if pull is not None and pull.report_code and pull.fight_id
                    else None
                ),
            )
        )

    # --------------------------------------------------

    def apply(self, pull, focus=None):
        """
        `pull` ist ein `LastPull` - aus der Sitzung oder aus dem
        Archiv, die Karte behandelt beide gleich.

        `focus` ist die aufgezeichnete Bewertung **genau dieses** Pulls
        (`(Bereich, Sterne)`) oder `None`. Sie kommt von aussen und
        wird hier nicht berechnet: die Übersicht darf keinen Kampf
        auswerten, dafür müsste sie ihn beim Bot holen, und das kostet
        Minuten. Woher sie kommt, steht in
        `OverviewPage._pull_focus()`.

        Der Leerzustand ist der Fall "es gibt wirklich keinen": kein
        Pull in dieser Sitzung, kein Bericht beim Bot, kein
        Zwischenspeicher. Er sagt weiterhin, woran es liegt.
        """

        self._pull = pull if pull is not None and pull.known else None

        self.open_pull.setEnabled(self._pull is not None)

        self.open_lesson.setEnabled(self._pull is not None)

        if pull is None or not pull.known:

            self.timestamp.setText("")

            self.boss.setText("Noch kein Pull")

            self.result.setText(
                "Sobald ein Kampf endet, steht sein Ergebnis hier."
            )

            self.sparkline.setValues([])

            self._apply_focus(None)

            self.lesson_title.setText("Noch nichts auszuwerten.")

            self.lesson_reason.setText(
                "Nach dem ersten ausgewerteten Pull steht hier, woran "
                "zu arbeiten sich am meisten lohnt - mit den "
                "Messwerten, aus denen sich das ergibt."
            )

            return

        self.timestamp.setText(when_text(pull))

        self.boss.setText(pull.boss or "Kampf")

        self.result.setText(result_text(pull))

        #
        # Die Kurve zeigt den geschafften Bossanteil der letzten
        # Versuche an demselben Boss - die eine Linie, die "wird es
        # besser?" beantwortet.
        #

        self.sparkline.setValues(list(pull.trend))

        self._apply_focus(focus)

    def _apply_focus(self, focus):
        """
        Der Fokus - oder ehrlich, dass es noch keinen gibt.

        **Es wird nichts geschätzt.** Liegt für diesen Pull keine
        aufgezeichnete Bewertung vor, bleibt die Sternreihe leer und der
        Satz sagt, was zu tun ist, um eine zu bekommen. Ein
        "schwächster Bereich" ohne Auswertung wäre geraten, und die
        leere Sternreihe daneben sähe ohne diesen Satz wie ein Urteil
        aus.
        """

        if not focus:

            self.area.setText("—")

            self.rating.setStars(0)

            self.lesson_title.setText("Dieser Pull ist noch nicht bewertet.")

            self.lesson_reason.setText(
                "„Pull ansehen“ lädt ihn ins Raid Center; unter "
                "*Lernen* stehen dann Bewertung, Baustellen und die "
                "Lektion dazu. Die vollständige Auswertung eines Pulls "
                "holt der Bot erst auf Anforderung."
            )

            return

        label, stars = focus

        self.area.setText(label)

        self.rating.setStars(int(stars))

        self.lesson_title.setText(f"{label} ist dein schwächster Bereich.")

        self.lesson_reason.setText(
            "„Daraus lernen“ öffnet diesen Pull unter *Lernen* - mit "
            "der Begründung, der passenden Lektion und dem Moment im "
            "Kampf, an dem es passiert ist."
        )


