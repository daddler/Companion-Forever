"""
Ein Lader für eine Auswertung des Spielstands (Berufe, Fehler).

Dasselbe Vorgehen wie `inventory_loader.py`: kurzlebiger Thread, nur
lesen, wenn sich eine Datei geändert hat, Ergebnis über ein Signal in
den Hauptthread. Der Bestand behält seinen eigenen Lader (Übersicht
und Bestandsseite teilen ihn); dieser hier ist für Seiten, denen eine
`load(wow_path, addon_path)`-Funktion reicht.
"""

from __future__ import annotations

import threading

from PySide6.QtCore import QObject, Signal

from gui.controllers.inventory_loader import _files_stamp


class SavedDataLoader(QObject):

    changed = Signal(object)

    busy = Signal(bool)

    _done = Signal(object, object)

    def __init__(self, manager, load, empty, name: str):

        super().__init__()

        self.manager = manager

        self._load = load

        self._empty = empty

        self._name = name

        self.result = empty()

        self._stamp = None

        self._running = False

        self._done.connect(self._on_done)

    def request(self, force: bool = False):

        if self._running:
            return

        self._running = True

        self.busy.emit(True)

        state = self.manager.state

        wow_path = getattr(state, "wow_path", None)

        addon_path = getattr(state, "addon_path", None)

        previous = None if force else self._stamp

        def worker():

            try:

                stamp = _files_stamp(wow_path)

                if stamp == previous:

                    self._done.emit(None, stamp)

                    return

                result = self._load(wow_path, addon_path)

            except Exception as exc:

                stamp, result = None, self._empty()

                result.error = str(exc)

            self._done.emit(result, stamp)

        threading.Thread(target=worker, name=self._name, daemon=True).start()

    def _on_done(self, result, stamp):

        self._running = False

        self.busy.emit(False)

        if result is None:
            return

        self._stamp = stamp

        self.result = result

        if result.error:

            logger = getattr(self.manager, "logger", None)

            if logger is not None:
                logger.warning(f"Spielstand nicht vollständig lesbar: {result.error}")

        self.changed.emit(result)


def auction_loader(manager) -> SavedDataLoader:
    """
    Der Lader der Preisverläufe (`core/auction_history.py`), einer je Manager.

    Das Fenster stößt ihn einmal beim Start an, sobald der Spielordner
    bekannt ist - WeintCodex behält nur 7 Tage, und wer die Seite
    *Berufe* länger nicht öffnet, verlöre sonst die Tage dazwischen.
    """

    loader = getattr(manager, "_auction_loader", None)

    if loader is None:

        from core import auction_history

        loader = SavedDataLoader(manager, auction_history.load, auction_history.AuctionHistory, "AuctionLoad")

        try:
            manager._auction_loader = loader

        except AttributeError:
            pass

    return loader
