import hashlib
from pathlib import Path

import httpx

from core.paths import Paths


#
# Wie viele heruntergeladene Dateien im Download-Ordner liegen bleiben.
# Sie lassen sich jederzeit neu laden; bis 5.1.2 wurde trotzdem nie
# eine gelöscht. Siehe prune_downloads().
#

MAX_DOWNLOADS = 3


def prune_downloads(folder: Path, keep: int = MAX_DOWNLOADS) -> list[Path]:
    """
    Löscht alle Dateien in `folder` bis auf die `keep` jüngsten
    (nach Änderungszeit - die Namen folgen keinem gemeinsamen Muster).

    Eine Datei, die sich nicht löschen lässt (etwa ein Windows-
    Installer, der gerade noch läuft), bleibt liegen; Aufräumen darf
    weder einen Download noch den Start scheitern lassen.
    """

    folder = Path(folder)

    if not folder.is_dir():
        return []

    try:
        files = sorted(
            (entry for entry in folder.iterdir() if entry.is_file()),
            key=lambda entry: entry.stat().st_mtime,
            reverse=True,
        )

    except OSError:
        return []

    removed: list[Path] = []

    for entry in files[max(keep, 0):]:

        try:
            entry.unlink()

        except OSError:
            continue

        removed.append(entry)

    return removed


class ChecksumError(Exception):
    pass


class Downloader:

    # --------------------------------------------------

    def download(
        self,
        url: str,
        destination: Path,
        expected_sha256: str | None = None,
    ):
        """
        Lädt "url" nach "destination". Ist "expected_sha256" gesetzt,
        wird die Datei während des Streamens gehasht und der Digest
        danach mit dem erwarteten Wert verglichen - bei Abweichung
        wird die (potenziell manipulierte oder beschädigte) Datei
        gelöscht und ChecksumError geworfen, statt sie an den
        Aufrufer zurückzugeben.
        """

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        hasher = hashlib.sha256()

        with httpx.stream(
            "GET",
            url,
            follow_redirects=True,
            timeout=60,
        ) as response:

            response.raise_for_status()

            with open(destination, "wb") as file:

                for chunk in response.iter_bytes():

                    file.write(chunk)
                    hasher.update(chunk)

        if expected_sha256:

            actual = hasher.hexdigest().lower()
            expected = expected_sha256.strip().lower()

            if actual != expected:

                destination.unlink(missing_ok=True)

                raise ChecksumError(
                    f"Prüfsumme stimmt nicht überein für {destination.name} "
                    f"(erwartet {expected}, erhalten {actual})."
                )

        #
        # Nur im eigenen Download-Ordner aufräumen: das Linux-Self-Update
        # lädt neben die laufende AppImage, und dort liegen Dateien des
        # Nutzers, die diese Anwendung nichts angehen.
        #

        if destination.parent.resolve() == Paths.downloads().resolve():
            prune_downloads(destination.parent)

        return destination