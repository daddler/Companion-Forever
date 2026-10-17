from pathlib import Path
import os
import platform


class Paths:

    # --------------------------------------------------
    # Basisverzeichnis
    # --------------------------------------------------

    @staticmethod
    def base() -> Path:

        system = platform.system()

        #
        # Linux
        #

        if system == "Linux":

            return (
                Path.home()
                / ".local"
                / "share"
                / "WeintCompanion"
            )

        #
        # Windows
        #

        if system == "Windows":

            local = os.getenv("LOCALAPPDATA")

            if local:

                return (
                    Path(local)
                    / "WeintCompanion"
                )

        #
        # macOS - der vom System vorgesehene Ort für Anwendungsdaten.
        # Bis 5.2 landete der Mac im Fallback unten; wer die App dort
        # schon aus dem Quellcode laufen hatte, behält seinen Ordner.
        #

        if system == "Darwin":

            legacy = Path.home() / ".weintcompanion"

            if legacy.is_dir():
                return legacy

            return (
                Path.home()
                / "Library"
                / "Application Support"
                / "WeintCompanion"
            )

        #
        # Fallback
        #

        return (
            Path.home()
            / ".weintcompanion"
        )

    # --------------------------------------------------

    @staticmethod
    def cache() -> Path:

        path = (
            Paths.base()
            / "cache"
        )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    # --------------------------------------------------

    @staticmethod
    def downloads() -> Path:

        path = (
            Paths.cache()
            / "downloads"
        )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    # --------------------------------------------------

    @staticmethod
    def backups() -> Path:

        path = (
            Paths.cache()
            / "backups"
        )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    # --------------------------------------------------

    @staticmethod
    def logs() -> Path:

        path = (
            Paths.cache()
            / "logs"
        )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    # --------------------------------------------------

    @staticmethod
    def reports() -> Path:
        """
        Ausgewertete Kämpfe des Raidlog Analyzers.

        Bewusst unterhalb von cache(): die Berichte lassen sich aus
        dem Combat-Log jederzeit neu erzeugen und dürfen deshalb
        gelöscht werden. Nutzerdaten (z. B. der Academy-Fortschritt)
        gehören dagegen nach config().
        """

        path = (
            Paths.cache()
            / "reports"
        )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    # --------------------------------------------------

    @staticmethod
    def config() -> Path:

        path = (
            Paths.base()
            / "config"
        )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path