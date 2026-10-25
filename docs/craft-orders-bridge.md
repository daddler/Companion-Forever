# Aufträge der Gilde: Vertrag zwischen Bot, Companion und Addon

„Stell mir das her“ – ein Spieler sieht im Discord, dass ein anderer ein
Rezept kann, und gibt einen Auftrag auf. Der Hersteller bekommt ihn
sofort per Discord-DM und in der Companion, im Spiel beim nächsten
Einloggen oder `/reload`. Status setzen kann er an allen drei Stellen.
Sichtbar ist ein Auftrag nur für Besteller und Hersteller.

| Seite | Datei |
|-------|-------|
| Bot, Regeln und Bestand | `services/craft_orders.py` (die **einzige** Stelle, die entscheidet, wer was darf) |
| Bot, Discord (Anlegen aus *Rezept suchen*, DMs, Knöpfe) | `services/order_views.py` |
| Bot, Endpunkte | `services/sync_server.py` (`companion_orders`, `companion_order_status`) |
| Companion | `core/craft_orders.py`, Abschnitt *Aufträge* auf `gui/pages/professions.py`, Ansage `gui/main_window.py` (`_announce_orders`), Weitergabe der Klicks aus dem Spiel `core/sync_manager.py` |
| Addon | `modules/craftorders.lua` (Fenster, `/wc aufträge`), Inbox-Behandler in `modules/companion.lua` |

## Status

```
open ──Annehmen──► accepted ──Erledigt──► done
  │ └──Erledigt──────────────────────────► done
  └──Ablehnen──► declined ◄──Ablehnen── accepted
open/accepted ──Stornieren (nur Besteller)──► cancelled
```

Derselbe Status zweimal ist **kein Fehler** (`changed: false`) – Codex
und Companion können denselben Klick melden. Erledigte, abgelehnte und
stornierte Aufträge fallen nach 14 Tagen heraus.

## Bot ↔ Companion

```
GET /companion/orders
Authorization: Bearer <companion_token>
→ {"status": "ok", "orders": [
    {"id": 12, "role": "crafter", "recipe": "Runenstoffbeutel",
     "character": "Weintmage", "profession": "Schneiderei", "quantity": 4,
     "note": "per Post", "mats": true, "status": "open",
     "requester_name": "Fabi", "requester_id": "…", "crafter_id": "…",
     "created_at": 1761400000, "updated_at": 1761400000}
  ]}
```

`role` sagt, was der Fragende in diesem Auftrag ist (`crafter` oder
`requester`). Discord-IDs immer als Zeichenkette.

```
POST /companion/orders/<id>/status
{"status": "accepted", "via": "companion" | "codex"}
```

| Antwort | Companion |
|---|---|
| 200 `{"status":"ok","changed":bool,"order":{…}}` | fertig, neu abrufen |
| 409 / 400 / 404 | geht nicht (mehr) – **verwerfen**, nicht wiederholen |
| 502 / 503 / Netz | später noch einmal |
| 401 | `note_auth_rejected()` (nie sofort entkoppeln) |

Wie bei `/sync`: **„ok“ erst, wenn die Sicherung geschrieben ist**
(privater Thread `auftraege-sicherung` im Berufe-Channel). Scheitert sie,
legt der Bot den alten Status zurück – sonst sähe der nächste Versuch
„keine Änderung“ und bekäme ein „ok“ ohne Sicherung.

Die Companion fragt höchstens jede Minute. Neu ist ein eingehender
offener Auftrag, den sie seit dem Start noch nicht gesehen hat (beim
ersten Abruf nach dem Start ist nichts „neu“).

## Companion → Addon

Inbox-Kanal `orders`, Typ `craft_orders`, **immer der volle Stand**:

```lua
{ type = "craft_orders", payload = {
    count = 1,
    orders = {
        { id = 12, role = "crafter", recipe = "Runenstoffbeutel",
          character = "Weintmage", quantity = 4, mats = true,
          status = "open", from = "Fabi", note = "per Post" },
    },
} }
```

Nur offene und angenommene. `count = 0` mit leerer Liste heißt „keine“
– eine leere Nutzlast ließe die Inbox weg, und im Spiel bliebe der alte
Stand stehen.

## Addon → Companion

Ein Klick im Spiel reiht `craft_order_status` mit der Nutzlast
`"<id>|<status>"` in `WeintCompanionDB.queue`. Das Spiel schreibt die
Datei beim Ausloggen oder `/reload`; die Companion reicht die Nachricht
an `POST …/status` (`via: "codex"`) und löscht sie bei 200 oder 409,
behält sie bei Netz- und Serverfehlern. Bis die Antwort des Bots im
Spiel ankommt, zeigt das Addon den Auftrag mit „wird gemeldet“ und
ohne Knöpfe.

## Echtzeit – was geht und was nicht

Das Spiel lässt Addons zur Laufzeit keine Dateien lesen. Ein Auftrag
erreicht WeintCodex deshalb erst beim Einloggen oder `/reload`. Sofort
erfährt der Hersteller ihn per Discord-DM und durch die Ansage der
Companion; das Fenster im Spiel hat dafür den Knopf „Neue Aufträge
holen“ (`/reload` über den sicheren Makroknopf).
