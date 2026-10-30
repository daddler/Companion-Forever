# Auktionspreise → Preisverläufe (`WeintCodex_SavedData.auction`)

Nur lesend, eine Richtung: WeintCodex schreibt, die Companion liest beim
Öffnen der Seite *Berufe* (`core/auction_history.py`).

| Feld | Inhalt | Seit |
|---|---|---|
| `auction["Realm|Seite"]` | Seite: `Alliance`, `Horde`, `Neutral` | Addon 6.17.0.0 |
| `.items[id]` | gepackt: Preis·1e7 + Menge·1e4 + Tag (+5000 = von Spielern), Tag 0 = 1.1.2026 | 6.17.0.0 |
| `.hist[id]` | `"Tag:Preis,…"`, eigene Scans, 7 Tage | — |
| `.names[id]` | Name aus dem Scan, nur für Gegenstände mit Preis | 1.8.1.0 |

Regeln: Preise „von Spielern“ gehen nicht in den Verlauf. Die Companion
behält den Verlauf in `auction_history.json` im eigenen Datenordner
(365 Tage), nie im Spielstand. Ändert das Addon `AP.Pack`, ändert sich
`unpack()` hier im selben Zug.
