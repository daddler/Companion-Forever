"""
Bossbezogene Lektionen.

Die Ebene, auf der aus "vermeidbarer Schaden" konkreter Lernstoff
wird: die Fähigkeiten hier sind dieselben, die
analyzer/data/avoidable.py als vermeidbar einordnet. Damit schließt
sich der Kreis - ein Treffer in der Analyse führt zu einer Lektion,
die genau diesen Treffer behandelt, und der Trainingsplan prüft
anschließend selbst, ob er ausgeblieben ist.

Der Schlüssel ist der **englische** Bossname, wie ihn WarcraftLogs
und das Combat-Log liefern - dieselbe Konvention wie in
analyzer/data/encounters.py.

ABGEDECKT: NOCH NICHTS
----------------------

`ENCOUNTER_LESSONS` ist leer, weil `analyzer/data/avoidable.py` es
ist - und die Kopplung unten beschreibt genau, warum das richtig so
ist: eine Lektion zu einem Boss, dessen Fähigkeiten nirgends
eingeordnet sind, könnte nie geprüft werden. Sobald die Bosse von
Forever bekannt und ihre Mechaniken eingeordnet sind, entsteht hier
je Boss ein Eintrag; vorher wäre jeder eine Behauptung.

Es stehen hier nur Kämpfe, für die auch Referenzdaten in
analyzer/data/avoidable.py hinterlegt sind - eine Lektion zu einem
Boss, dessen Fähigkeiten nirgends eingeordnet sind, könnte nie
geprüft werden und bliebe dauerhaft auf "keine Daten" stehen. Ein
Test hält diese Kopplung fest.
"""

from __future__ import annotations

from analyzer.academy.models import (
    CATEGORY_MECHANICS,
    CATEGORY_MOVEMENT,
    CATEGORY_SURVIVAL,
    CHECK_AT_MOST,
    Lesson,
    LessonCheck,
)
from analyzer.models import MECHANIC_INTERRUPT, MECHANIC_MOVEMENT


def _no_hits(label: str) -> LessonCheck:
    """
    "Keine vermeidbaren Treffer" - das mit Abstand häufigste
    Kriterium bossbezogener Lektionen.
    """

    return LessonCheck(
        metric="avoidable_hits",
        comparison=CHECK_AT_MOST,
        target=0.0,
        unit="×",
        label=label,
    )


ENCOUNTER_LESSONS: dict[str, tuple[Lesson, ...]] = {}
