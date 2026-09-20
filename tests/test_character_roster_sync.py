"""
Die Twinkliste auf dem Weg zum Bot.

Sie ist die **einzige** Charakterauskunft, die diese App überhaupt
weitergibt: "Meine Charaktere" und "Vorbereitung" lesen
`character_sheet`, und das bleibt lokal (siehe
`docs/character-sheet-bridge.md`). Was hinausgeht, ist Name, Klasse,
Realm - und seit 5.0.3 die Spielversion.

Die gehört dazu, weil **ein** Bot **zwei** Companion-Fassungen bedient:
die für Mists of Pandaria und diese hier. Beide melden mit demselben
Discord-Konto in dieselbe Tabelle, und beide ersetzen dort ihre eigene
Meldung vollständig. Ohne die Spielversion ersetzt jede die Charaktere
der anderen - im Fünf-Minuten-Takt, und der Kalender-Invite benennt
dann je nach Zufall einen Charakter aus dem falschen Spiel.
"""

import pytest

httpx = pytest.importorskip("httpx")

from core import character_sync_client
from core.character_sync_client import CharacterSyncClient
from core.wow_clients import DEFAULT_CLIENT_ID


class _Antwort:

    status_code = 200

    @staticmethod
    def json():
        return {"status": "ok"}


@pytest.fixture
def gesendet(monkeypatch):
    """
    Ein verknüpftes Konto und ein Briefkasten statt des Bots.
    """

    monkeypatch.setattr(
        character_sync_client.DiscordAccountStore,
        "load",
        lambda self: {"companion_token": "wc1.aaa.bbb"},
    )

    briefkasten = {}

    def _post(url, json=None, headers=None, timeout=None):

        briefkasten["url"] = url
        briefkasten["body"] = json

        return _Antwort()

    monkeypatch.setattr(character_sync_client.httpx, "post", _post)

    return briefkasten


def test_die_spielversion_geht_mit(gesendet):

    assert CharacterSyncClient().send(
        "Njiah|WARRIOR|Everlook,Magi|MAGE|Everlook",
        DEFAULT_CLIENT_ID,
    )

    assert gesendet["body"]["wow_client"] == DEFAULT_CLIENT_ID

    assert [
        eintrag["name"]
        for eintrag in gesendet["body"]["characters"]
    ] == ["Njiah", "Magi"]


def test_ohne_angabe_bleibt_es_bei_der_alten_meldung(gesendet):
    """
    Die Angabe ist auf der Bot-Seite optional - eine Companion ohne
    sie bleibt gültig. Diese Zeile hält fest, dass ein Aufrufer, der
    sie nicht mitgibt, nichts anderes behauptet, statt sich selbst als
    irgendeine Spielversion auszugeben.
    """

    assert CharacterSyncClient().send("Njiah|WARRIOR|Everlook")

    assert gesendet["body"]["wow_client"] == ""
