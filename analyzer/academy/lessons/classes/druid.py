"""
Lektionen für Druiden.

**Noch keine.** Forever überarbeitet jede Klasse und jeden
Talentbaum; welche Fähigkeiten Druiden danach haben und wie sie
zusammenspielen, ist zum Zeitpunkt dieses Eintrags nicht
veröffentlicht. Der Katalog aus Mists of Pandaria stehen zu lassen
hiesse, jemandem eine Rotation beizubringen, die es nicht gibt.

Leer ist hier kein Mangel, sondern die vorgesehene Rückfallebene:
`analyzer/academy/lessons/generic.py` und `roles.py` gelten für jede
Klasse und jede Rolle, und solange hier nichts steht, bekommt ein
Druide genau die - einen sinnvollen Plan, nur keinen
klassenspezifischen.

ERWEITERN: je Spezialisierung ein Eintrag unten. Die Prüfbausteine
in `_common.py` (`uptime_check`, `cooldown_check`,
`buff_uptime_check`, `hot_uptime_check`, `interrupt_check`,
`defensive_check`, `dispel_check`) bleiben unverändert nutzbar; eine
Lektion ohne `checks` ist erlaubt und bedeutet "nicht messbar, zum
Lesen und selbst Abhaken".

Der leere Schlüssel `""` gilt für die ganze Klasse - dort gehört
hin, was jede Spezialisierung teilt (Nutzfähigkeiten, Rettungen).
"""

from analyzer.academy.lessons.classes._common import Lesson

CLASS_NAME = "Druid"

SPEC_LESSONS: dict[str, tuple[Lesson, ...]] = {

    "Gleichgewicht": (),

    "Wilder Kampf": (),

    "Wiederherstellung": (),


    "": (),

}
