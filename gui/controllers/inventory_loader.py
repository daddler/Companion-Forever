"""
Ein Lader für den Bestand, den Übersicht und Bestandsseite teilen.

Der Spielstand wird in einem kurzlebigen Thread gelesen (er kann mit
den Auktionspreisen mehrere Megabyte haben) und nur, wenn sich eine
der Dateien geändert hat. Das Ergebnis kommt über ein Signal in den
Hauptthread - Widgets dürfen nur dort angefasst werden.

Eine Instanz je Manager (`inventory_loader(manager)`), damit zwei
Seiten dieselbe Datei nicht zweimal lesen.
"""

from __future__ import annotations

import threading

from PySide6.QtCore import QObject, Signal

from core.backup import saved_variable_files
from core.inventory import Inventory, load


def _files_stamp(wow_path) -> tuple:

    stamp = []

    for path in saved_variable_files(wow_path):

        try:
            info = path.stat()

        except OSError:
            continue

        stamp.append((str(path), info.st_mtime_ns, info.st_size))

    return tuple(stamp)


class InventoryLoader(QObject):

    #
    # Neuer Bestand (auch bei Fehlern - `Inventory.error` sagt dann,
    # was war). Kommt nicht, wenn sich nichts geändert hat.
    #

    changed = Signal(object)

    #
    # Lesen läuft / ist fertig - für Knöpfe, die sich sperren.
    #

    busy = Signal(bool)

    _done = Signal(object, object)

    def __init__(self, manager):

        super().__init__()

        self.manager = manager

        self.inventory = Inventory()

        self._stamp = None

        self._running = False

        self._done.connect(self._on_done)

    def request(self, force: bool = False):

        if self._running:
            return

        self._running = True

        self.busy.emit(True)

        wow_path = getattr(self.manager.state, "wow_path", None)

        previous = None if force else self._stamp

        def worker():

            try:

                stamp = _files_stamp(wow_path)

                if stamp == previous:

                    self._done.emit(None, stamp)

                    return

                inventory = load(wow_path)

            except Exception as exc:

                #
                # Nie den Thread lautlos sterben lassen: ein Fehler ist
                # ein Ergebnis, und die Seite sagt ihn.
                #

                stamp, inventory = None, Inventory(error=str(exc))

            self._done.emit(inventory, stamp)

        threading.Thread(target=worker, name="InventoryLoad", daemon=True).start()

    def _on_done(self, inventory, stamp):

        self._running = False

        self.busy.emit(False)

        if inventory is None:
            return

        self._stamp = stamp

        self.inventory = inventory

        if inventory.error:

            logger = getattr(self.manager, "logger", None)

            if logger is not None:
                logger.warning(f"Bestand nicht vollständig lesbar: {inventory.error}")

        self.changed.emit(inventory)


def inventory_loader(manager) -> InventoryLoader:

    loader = getattr(manager, "_inventory_loader", None)

    if loader is None:

        loader = InventoryLoader(manager)

        try:
            manager._inventory_loader = loader

        except AttributeError:
            pass

    return loader
