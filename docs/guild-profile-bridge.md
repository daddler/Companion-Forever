# Berufe & Twinks: Vertrag zwischen Companion und Bot

`POST /companion/profile` – jede Companion meldet die Charaktere ihres
Spielers mit Stufe, Klasse, Berufen und bekannten Rezepten. Der Bot
zeigt das im Discord als Dauernachricht „📜 Berufe & Twinks“ im
Berufe-Channel (`PROFESSION_CHANNEL_ID`), mit den Knöpfen *Rezept
suchen* und *Spieler ansehen*.

| Seite | Datei |
|-------|-------|
| Companion, sendend | `core/guild_profile_sync.py` (Brücken-Karte „Berufe & Twinks“, Schlüssel `profile_sync_enabled`, Vorgabe an) |
| Bot, Endpunkt | `services/sync_server.py` (`companion_profile`) |
| Bot, Bestand | `services/guild_profiles.py` |
| Bot, Discord | `services/profession_board.py` |
| Addon (Quelle) | `WeintCodex_SavedData.professions` – gelesen von `core/professions.py`, das Addon selbst ist nicht beteiligt |

## Anfrage

```
POST /companion/profile
Authorization: Bearer <companion_token>
```

```json
{
  "wow_client": "forever",
  "characters": [
    {
      "name": "Weintmage",
      "realm": "Everlook",
      "class": "MAGE",
      "level": 34,
      "professions": [
        { "key": "tailoring", "name": "Schneiderei", "rank": 215, "max": 225,
          "scanned": true, "recipes": ["Leinenstoffbeutel", "Runenstoffbeutel"] },
        { "key": "enchanting", "name": "Verzauberkunst", "rank": null, "max": null,
          "scanned": false }
      ]
    }
  ]
}
```

## Regeln

- **Eine Meldung ist der vollständige Stand des Spielers** und ersetzt
  die vorige ganz. Ein verlernter Beruf, ein ausgeblendeter Twink
  verschwinden damit auch aus dem Discord. **Eine leere Liste nimmt den
  Spieler ganz heraus** – wer (noch) keinen Charakter hat, zählt nicht
  als „gemeldet“.
- **Gemeldet wird nur, was der Spieler verfolgt**
  (`CharacterStore.characters()`: diese Spielversion, nicht
  ausgeblendet). Dieselbe Wahl wie beim Charakter-Roster.
- **`unknown ≠ 0`.** `rank: null` = Fertigkeit nie gelesen (Bot: „Stufe
  ?“), `scanned: false` = Berufsfenster nie offen, dann **kein**
  `recipes` – nicht „0 Rezepte“. `level: null` = Stufe unbekannt.
- **Rezeptnamen** kommen aus dem Bestand des installierten Addons
  (`data/professions.lua`). Ohne Namen steht `#<Zauber-ID>`, geraten
  wird keiner.
- **„ok“ erst, wenn die Dauernachricht samt Sicherung geschrieben ist.**
  Der Bot hat keinen dauerhaften Speicher; die Nachricht trägt den
  ganzen Stand als Anhang (`berufe_sicherung.dat`) an einer Nachricht
  im **privaten Thread** `berufe-sicherung` des Berufe-Channels – nicht
  an der sichtbaren Nachricht – und liest ihn beim Start zurück. Ein „ok“ davor wäre beim nächsten Deploy verloren.
- **Gesendet wird nur bei Änderung** (Fingerabdruck der Meldung);
  gelesen wird nur, wenn sich eine SavedVariables-Datei oder die
  Auswahl der Charaktere geändert hat, höchstens alle zwei Minuten.

## Antworten

| Status | Bedeutung | Companion |
|---|---|---|
| 200 `{"status":"ok","characters":n,"changed":bool}` | angenommen und gesichert | merkt sich den Fingerabdruck |
| 400 | Meldung unbrauchbar | – |
| 401 | Token ungültig | `note_auth_rejected()` (nie sofort entkoppeln, siehe `companion-auth.md`) |
| 404 | ältere Bot-Fassung | still, neuer Versuch nach 10 min |
| 502 | Discord-Nachricht nicht geschrieben | neuer Versuch nach 10 min; der Bot schreibt beim nächsten Mal auch ohne Änderung (`profession_board.dirty`) |
| 503 | kein Berufe-Channel / Bot nicht verbunden | neuer Versuch nach 10 min |

## Was im Discord steht

**Genau eine Nachricht** im Channel: Erklärung und drei Knöpfe – **„N Spieler gemeldet“**, *Rezept suchen*,
*Spieler ansehen*. Neue Meldungen ändern nur die Zahl im Knopf; der
Channel wächst nicht. Die Liste je Spieler (Discord-Anzeigename, eine
Zeile je Charakter: „Weintmage (34 Magier) – Schneiderei 215/225,
Verzauberkunst (Stufe ?)“) und alle Suchergebnisse sieht nur, wer
klickt – bei vielen Spielern mit Blättern. Bis Bot-Stand 1.1.0 standen
die Spieler als Seitennachrichten darunter; der Bot räumt sie beim
nächsten Schreiben weg.
