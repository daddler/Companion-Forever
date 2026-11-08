# Fehlerberichte: Addon → Companion → Bot (seit Addon 1.0.5.28 / Companion 1.0.5)

Wunsch des Projektinhabers: „Button zum Bug senden – der User klickt nur
darauf, und der Report kommt bei mir an.“

## Ablauf

1. **Addon** (`../Codex-Forever/ui/errors.lua`): Das Fehlerfenster hat den
   Knopf „Melden & neu laden“ – nur wenn eine Companion die Live-Datei
   schreibt (`WeintCodex_CompanionLive.writtenAt > 0`). Der Klick setzt am
   Eintrag in `WeintCodex_SavedData.errors`:
   `report = "pending"`, `reportAt` (Unix-Zeit), `client` („1.60.1 (70862)“),
   `locale`, `class` (englisch, z. B. `PRIEST`), `level`, `zone` – und lädt
   über den sicheren Makroknopf neu, damit das in der Datei steht.
2. **Companion** (`core/bug_report_sync.py`): liest bei jeder geänderten
   SavedVariables-Datei die Fehler (`core/addon_errors.py`), schickt jeden mit
   `report == "pending"` genau einmal. Schlüssel: Konto + `reportAt` +
   Fehlertext; gesendet erst nach HTTP 200, dann in `config.bug_reports_sent`
   (höchstens 200). Fehlschlag → erneut nach 2 Minuten. Dazu der Knopf
   „An Entwickler senden“ auf der Seite „Addon-Fehler“ (sofort, ohne Spiel).
3. **Bot** (`../WeintCodex-Bot/services/bug_reports.py`):
   `POST /companion/bug-report` mit Companion-Token; legt je Bericht einen
   **neuen** Beitrag im Forum `BUG_CHANNEL_ID` an (Standard
   `1565364479158390954`). „ok“ erst, wenn der Beitrag steht.

## Nutzlast

```json
{ "kind": "lua|blocked", "message": "…", "stack": "…", "count": 3,
  "first": "08.11.2026 09:45:09", "last": "…", "addon_version": "1.0.5.28",
  "client": "1.60.1 (70862)", "locale": "deDE", "class": "PRIEST",
  "level": "12", "zone": "Elwynn", "character": "<Kontoordner>",
  "companion_version": "1.0.5" }
```

Der Bot setzt `reporter` selbst (verknüpfter Discord-Name). Alles außer
`message` ist optional; Texte werden gekürzt (Titel 100, Beitrag 2000 Zeichen).

## Was nie mitgeht

Chat, Gold, Inventar, andere SavedVariables. Nur, was im Fehlerbericht des
Addons steht.
