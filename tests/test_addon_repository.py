"""
Aus welchem Repository holt diese App das Addon?

**Warum es diese Prüfung gibt.** WeintCodex gibt es zweimal:
`daddler/WeintCodex` für Mists of Pandaria Classic und
`daddler/Codex-Forever` für Forever. Beide heissen im Spiel
"WeintCodex", beide liefern ein ZIP mit einem Ordner `WeintCodex` und
einer `WeintCodex.toc` darin, und beide werden über denselben
Update-Weg installiert.

Genau deshalb wäre die Verwechslung **still**: der Download läuft, die
Prüfsumme stimmt, `Installer._find_addon_folder()` findet seinen
Ordner, das Addon landet im Spielordner - und ist für die falsche
Spielfassung gebaut. Nichts an diesem Weg schlägt fehl. Auffallen
würde es erst im Spiel, an einer Oberfläche, die von Sockeln und
Umschmieden spricht.

Geprüft wird **strukturell** statt über eine Instanz: ein
`CompanionManager()` zieht Qt, die Konfiguration, den Discord-Zustand
und ein halbes Dutzend weiterer Bausteine nach sich, und keiner davon
hat mit dieser Frage etwas zu tun. Dieselbe Bauart wie die übrigen
AST-Prüfungen dieses Ordners.
"""

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

#
# Die beiden Repositories dieser Fassung. Sie stehen hier ausgeschrieben
# und nicht als Import: eine Prüfung, die ihren Sollwert aus derselben
# Datei liest, die sie prüft, kann nicht fehlschlagen.
#

ADDON_REPO = "Codex-Forever"

COMPANION_REPO = "Companion-Forever"

MOP_REPO = "WeintCodex"


def _github_updater_calls(relative: str) -> list[dict]:
    """
    Alle `GitHubUpdater(...)`-Aufrufe einer Datei, als Zuordnung ihrer
    Schlüsselwortargumente auf die literalen Werte.
    """

    tree = ast.parse(
        (ROOT / relative).read_text(encoding="utf-8")
    )

    found = []

    for node in ast.walk(tree):

        if not isinstance(node, ast.Call):
            continue

        name = node.func

        if not (isinstance(name, ast.Name) and name.id == "GitHubUpdater"):
            continue

        found.append(
            {
                keyword.arg: keyword.value.value
                for keyword in node.keywords
                if isinstance(keyword.value, ast.Constant)
            }
        )

    return found


def test_the_addon_comes_from_the_forever_repository():
    """
    Die eine Zeile, deren Fehlgriff folgenlos aussieht und es nicht ist.
    """

    calls = _github_updater_calls("core/companion_manager.py")

    assert len(calls) == 1, (
        "Es gibt genau einen Update-Weg fürs Addon. Kommt ein zweiter "
        "dazu, muss diese Prüfung ihn kennen."
    )

    call = calls[0]

    assert call.get("owner") == "daddler"

    assert call.get("repo") == ADDON_REPO, (
        f"Das Addon wird aus {call.get('repo')!r} geholt, erwartet ist "
        f"{ADDON_REPO!r}. {MOP_REPO!r} ist die Fassung für Mists of "
        "Pandaria Classic - sie installiert sich klaglos und ist für "
        "das falsche Spiel gebaut."
    )

    assert call.get("repo") != MOP_REPO


def test_the_companion_updates_itself_from_its_own_repository():
    """
    Die Gegenprobe: die App darf sich nicht aus dem Addon-Repository
    aktualisieren, und das Addon nicht aus ihrem.
    """

    calls = _github_updater_calls("core/companion_updater.py")

    assert len(calls) == 1

    assert calls[0].get("repo") == COMPANION_REPO


def test_no_link_in_the_interface_points_at_the_mop_repository():
    """
    Die sichtbare Hälfte derselben Frage.

    Ein Knopf "GitHub öffnen", der auf die MoP-Fassung zeigt, schickt
    jeden, der nach dem Addon sucht, an die falsche Stelle - und zwar
    an eine, die echt aussieht und gepflegt ist.

    Ausgenommen sind Kommentare: dort steht das alte Repository
    absichtlich, nämlich als Begründung dafür, warum es NICHT das
    richtige ist.
    """

    offenders = []

    for path in sorted((ROOT / "gui").rglob("*.py")):

        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):

            if line.lstrip().startswith("#"):
                continue

            if f"github.com/daddler/{MOP_REPO}" in line:
                offenders.append(f"{path.relative_to(ROOT)}:{number}")

    assert not offenders, (
        "Diese Stellen verlinken noch das Addon für Mists of Pandaria: "
        + ", ".join(offenders)
    )
