"""
Nur EINE WeintCompanion je Benutzer und Rechner (1.0.8).

Anlass (Stream eines Spielers): nach einem Update von Codex schloss der
Spieler die Companion mit dem Kreuz - sie lief im Tray weiter -, startete
sie für das nächste Update per Doppelklick erneut, und am Ende liefen vier
Companions parallel. Vier Prozesse, die dieselben SavedVariables lesen und
schreiben, dieselbe Bot-Verbindung halten und dieselben Updates anbieten,
sind kein Komfort, sondern eine Quelle für verlorene Daten.

Wie es geht:
- Die erste Companion lauscht auf einem lokalen Kanal (`QLocalServer`:
  auf Windows eine benannte Pipe, auf Linux ein Socket), Name je Benutzer.
- Eine zweite Companion meldet sich dort mit "show" und beendet sich
  sofort. Die erste holt ihr Fenster aus dem Tray nach vorn.
- Beim Beenden schließt die erste den Kanal ZUERST - der Selbst-Update
  startet die neue Version, sobald die alte gegangen ist, und die neue
  darf sich dann nicht wegschicken lassen.
- Ein Kanal, der nach einem Absturz liegen geblieben ist (Linux: alte
  Socket-Datei), antwortet nicht; dann wird er entfernt und neu belegt.

Netzwerk ist das nicht: der Kanal ist nur lokal und nur für diesen
Benutzer erreichbar.
"""

from __future__ import annotations

import getpass
import hashlib

from PySide6.QtNetwork import QLocalServer, QLocalSocket


SHOW_MESSAGE = b"show\n"
CONNECT_TIMEOUT_MS = 500


def server_name() -> str:
    """Name des Kanals - je Benutzer, ohne Sonderzeichen im Namen."""

    try:
        user = getpass.getuser()
    except Exception:
        user = "user"

    digest = hashlib.sha1(user.encode("utf-8", "replace")).hexdigest()[:12]

    return f"WeintCompanion-{digest}"


class SingleInstance:

    def __init__(self, name: str | None = None):

        self.name = name or server_name()
        self.server: QLocalServer | None = None
        self._on_show = None

    # --------------------------------------------------

    def notify_running(self) -> bool:
        """
        Läuft schon eine Companion? Dann ihr "show" schicken und True.
        False: keine erreichbar - diese wird die erste.
        """

        socket = QLocalSocket()
        socket.connectToServer(self.name)

        if not socket.waitForConnected(CONNECT_TIMEOUT_MS):
            return False

        socket.write(SHOW_MESSAGE)
        socket.flush()
        socket.waitForBytesWritten(CONNECT_TIMEOUT_MS)
        socket.disconnectFromServer()

        return True

    # --------------------------------------------------

    def listen(self, on_show) -> bool:
        """
        Den Kanal belegen. on_show() läuft, wenn eine zweite Companion
        gestartet wird. True, wenn der Kanal belegt ist.
        """

        self._on_show = on_show

        server = QLocalServer()

        if not server.listen(self.name):

            #
            # Liegengebliebener Kanal (Absturz): niemand antwortet -
            # notify_running() war davor schon False. Entfernen und
            # noch einmal.
            #

            QLocalServer.removeServer(self.name)

            if not server.listen(self.name):
                return False

        server.newConnection.connect(self._accept)

        self.server = server

        return True

    # --------------------------------------------------

    def _accept(self):

        server = self.server

        if server is None:
            return

        while server.hasPendingConnections():

            socket = server.nextPendingConnection()

            if socket is None:
                break

            if socket.bytesAvailable() or socket.waitForReadyRead(CONNECT_TIMEOUT_MS):
                data = bytes(socket.readAll())
            else:
                data = b""

            socket.disconnectFromServer()
            socket.deleteLater()

            if data.startswith(SHOW_MESSAGE.strip()) and self._on_show is not None:
                try:
                    self._on_show()
                except Exception as exc:
                    print(f"[WeintCompanion] Fenster nicht geholt: {exc}")

    # --------------------------------------------------

    def close(self):
        """Kanal freigeben (beim Beenden, VOR dem Aufräumen)."""

        if self.server is not None:

            self.server.close()

            self.server = None
