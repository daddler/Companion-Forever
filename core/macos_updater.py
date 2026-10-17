from pathlib import Path
import shutil
import stat
import sys

from core.paths import Paths


class MacOSUpdater:
    """
    Bereitet das Selbst-Update unter macOS vor.

    Ein laufendes `.app`-Bundle lässt sich nicht sauber von innen
    ersetzen. Deshalb wird - wie unter Linux - ein kleines Skript
    (`packaging/macos/updater.sh`) aus dem Bundle heraus nach
    `Paths.cache()` kopiert und von dort gestartet: es wartet auf das
    Ende dieses Prozesses, tauscht das Bundle gegen das aus dem `.dmg`
    und startet die neue Fassung.

    Das Skript darf nicht im Bundle selbst liegen bleiben, denn genau
    das Bundle wird ja ausgetauscht.
    """

    def prepare(self) -> Path:

        if getattr(sys, "frozen", False):

            base = Path(sys._MEIPASS)

        else:

            base = Path(__file__).resolve().parent.parent

        source = (
            base
            / "packaging"
            / "macos"
            / "updater.sh"
        )

        if not source.exists():

            raise FileNotFoundError(
                f"Updater nicht gefunden: {source}"
            )

        target = Paths.cache() / "update-macos.sh"

        target.unlink(missing_ok=True)

        shutil.copy2(source, target)

        target.chmod(
            target.stat().st_mode
            | stat.S_IXUSR
            | stat.S_IXGRP
            | stat.S_IXOTH
        )

        return target
