# Charakteridentität & Notfall-Backup: Vertrag zwischen Bot, Companion und WeintAdmin

Diese Datei bündelt drei verwandte, aber getrennte Bot-Endpunkt-Familien, die
alle die Frage "wer ist wer" oder "was stand gerade im Sign-up" beantworten:
`/companion/raid-roster`, `/companion/character-links`, `/companion/raid-
signups` (WeintAdmin). Bot-Seite: `services/character_links.py`,
`services/admin_sync.py`, `services/raid_export_manager.py`,
`services/sync_server.py`. Companion-Seite: `core/character_links.py` (rein),
`core/character_links_client.py` (HTTP), `gui/pages/character_links.py`.

## Wer steckt hinter einem Discord-Konto? (`character_links.py`, Bot)

Der Kalender-Invite braucht einen echten Charakternamen (siehe
`wcimport-protocol.md`). Der Bot kannte ihn bisher nur über
`companion_characters` (gefüllt von `POST /companion/characters`, jeder
verlinkte Spieler meldet seine eigenen Twinks) — für alle anderen ging der
Discord-Anzeigename raus, der ingame nicht existiert.

`services/character_links.py` fügt eine **zweite, von Hand gesetzte** Quelle
hinzu und ist die eine Stelle, an der beide Quellen versöhnt werden. Die
Rangfolge (in `tests/test_character_links.py` gepinnt, ein Fehler hier wirft
keinen Fehler — er lädt die falsche Person ein):

1. manueller Eintrag, der zur Klasse passt
2. der eigene Bericht des Spielers, der zur Klasse passt
3. manueller Eintrag ohne Klasse (der Platzhalter)
4. → nichts, Rückfall auf den Discord-Namen

Die spezifischere Antwort gewinnt immer, gleich aus welcher Quelle; bei
gleicher Spezifität gewinnt die Raidleitung (die aktuellste Korrektur schlägt
einen möglicherweise wochenalten Bericht). Zwei strukturelle Punkte: eine
**eigene Tabelle**, nicht eine `source`-Spalte auf `companion_characters`
(das wird bei jedem Sync komplett ersetzt — ein manueller Eintrag dort würde
beim nächsten Sync des Spielers gelöscht); `class_token` ist immer `''`,
nie `NULL` (SQLite behandelt NULLs in einem zusammengesetzten Primärschlüssel
als paarweise verschieden — „Platzhalter ersetzen" würde sonst lautlos zu
„zweiten Platzhalter hinzufügen").

Zwei Frontends, beide raidlead-gated, beide über dieselbe Regel:
- `/weintcharakter setzen|entfernen|liste` (Discord, `cogs/character_links.py`)
- `GET/POST/DELETE /companion/character-links` (Companion-Seite
  `gui/pages/character_links.py`, `PageId.CHARACTER_LINKS`)

`liste`/die Companion-Seite zeigen **vor** dem Einladungslauf, welcher Name
für wen benutzt würde und woher er kommt — `build_link_overview(guild,
raid_id)` liegt bewusst in `raid_export_manager.py` und läuft durch dieselbe
Auflösung wie der Export, damit Übersicht und tatsächlicher Export nie
auseinanderlaufen.

**Welcher Raid?** `GET /companion/character-links` nimmt `?raid=<id>`
und antwortet ohne Angabe zum nächsten Raid. Laufen zwei Anmeldungen
nebeneinander, ist „der nächste" die zuletzt erstellte — die ältere war
über die Companion-Seite damit nicht mehr erreichbar (gemeldet mit
einem offenen 25er, zu dem später ein 10er kam). Die Seite schickt die
Kennung deshalb seit Companion 3.5.0 mit; die Liste der wählbaren Raids
kommt aus `/companion/raid-schedule` (`raid_ids`/`others`, siehe
`raid-schedule-bridge.md`) und **nicht** aus einer zweiten Aufzählung an
diesem Endpunkt. Ohne bekannte Kennung wird auch keine geschickt, und es
bleibt beim bisherigen Verhalten.

Die **Handeinträge selbst kennen keinen Raid**: sie gelten für den
Account, nicht für eine Anmeldung. `POST`/`DELETE` tragen deshalb
weiterhin keinen Raidparameter — nur das erneute Holen danach braucht
ihn, damit die Liste dieselbe bleibt.

**Companion-Seite: sperren, nicht verstecken.** Ohne Raidlead-Rolle
antwortet der Bot mit 403; das reist als eigenes Feld (`Overview.forbidden`)
und erklärt, wofür die Seite da wäre, statt sie unsichtbar zu machen (*lock,
don't hide*, wie `core/access.lua` im Addon). „0 offen" wird nie behauptet,
wo nichts gezählt wurde (`summary_text()`, dieselbe Linie wie `stars == 0`).
Nach jedem Schreiben wird der **ganze** Stand neu geholt statt eine Zeile
lokal nachzuziehen — der Bot entscheidet über den Vorrang. Jeder Abruf läuft
in einem kurzlebigen Thread mit Rückmeldung über ein Signal (`loaded`).

## Die eigene Meldung: `POST /companion/characters`

Jeder verknüpfte Spieler meldet seine eigene Twinkliste — keine
Raidlead-Rolle, sonst funktionierte der Klassen-Abgleich nur für den
Raidleiter. Der Rumpf:

```json
{
  "characters": [
    {"name": "Njiah", "class": "WARRIOR", "realm": "Everlook"}
  ],
  "wow_client": "forever"
}
```

Die Liste kommt aus der Twinkverwaltung des Addons (`character`-Meldung,
`Name|Klasse|Realm`, siehe `core/character_sync_client.py`) und **nicht**
aus der Charakterliste der Companion: `character_sheet` bleibt lokal
(siehe `character-sheet-bridge.md`). Der Bot legt sie in
`companion_characters` ab und ersetzt dabei vollständig, was dasselbe
Discord-Konto **für dieselbe Spielversion** zuletzt gemeldet hat.

**`wow_client` ist die Spielversion, aus der gemeldet wird**
(`Config.get_wow_client_id()`, also `"forever"`). Sie steht seit
Companion 5.0.3 dabei, und sie ist der Unterschied zwischen zwei
Listen und einer:

- Ein Bot bedient **zwei** Companion-Fassungen — die für Mists of
  Pandaria und die für Forever. Beide melden mit demselben Discord-Konto
  an denselben Endpunkt, beide im Takt ihres Sync-Intervalls.
- Ohne die Angabe ersetzte jede Meldung die der anderen. Wessen Sync
  zuletzt lief, dessen Charaktere standen da — alle fünf Minuten die
  anderen, und der Kalender-Invite benannte je nach Zufall einen
  Charakter aus dem Spiel, in dem dieser Raid nicht stattfindet.
- Derselbe Name in zwei Spielen sind **zwei** Charaktere. Die
  Spielversion gehört deshalb in den Primärschlüssel und nicht nur in
  eine Spalte daneben; Realmnamen wiederholen sich zwischen zwei
  Spielen ebenso wie Charakternamen.

**Das Feld ist optional, und das bleibt es.** Eine Companion, die es
nicht kennt (jede vor 5.0.3, und das ist die gesamte MoP-Fassung),
meldet weiter gültig; ihre Meldungen zählen als Spielversion
„unbekannt" (der Leerstring) und ersetzen einander wie bisher. Eine
Fassung, die die Version nennt, lässt sie in Ruhe — was dort
liegenbleibt, ist entweder die lebende Liste der alten Fassung oder
ein Rest davon, und das ist von der Bot-Seite aus nicht zu
unterscheiden. Ein Rest, den die neueste Meldung verdrängt, ist der
kleinere Schaden gegenüber einer gelöschten lebenden Liste.

**Bei der Auflösung filtert der Bot nicht nach Spielversion**
(`get_character_for_class()`), und das ist Absicht: dafür müsste sie am
*Raid* hängen, und ein Raid ist ein Discord-Beitrag mit Datum und
Anmeldungen — in welchem Spiel er stattfindet, weiss der Bot nirgends.
Es entscheidet der Zeitstempel: die neueste passende Meldung gewinnt,
also das Spiel, aus dem zuletzt gemeldet wurde. Solange der Bot keine
Spielversion am Raid kennt, ist das die beste Antwort, die sich geben
lässt, und sie wird von selbst richtig, sobald jemand wieder spielt.

## WeintAdmin-Brücke (`services/admin_sync.py`, Bot)

Ein viertes, unabhängiges Backup der laufenden Anmeldung — für den Fall, dass
sowohl die Discord-Snapshot-Mechanik (siehe unten) **als auch** alle drei
Nachrichten-Kopien gleichzeitig verschwinden (Summary-Nachricht und beide
Tages-Threads von Hand gelöscht, bevor der Bot neu startet). WeintAdmin ist
ein kleines Desktop-Tool, das der Raidlead selbst bedient: holt die laufende
Anmeldung per HTTP, cached sie lokal, und schreibt sie — nachdem der Raidlead
den Raid in Discord neu erstellt hat (`/weintraid`) — in den neuen Raid
zurück.

`GET /companion/raid-signups` und `POST /companion/raid-signups/restore`
(beide raidlead-gated wie `/companion/raid-roster`) sind dünne
HTTP-Wrapper um `services/admin_sync.py`. Bei parallelen Raids ist das Ziel
eine Wahl, kein Automatismus: `?raid=<id>` bzw. `raid_id` im Body wählen
einen; weggelassen bedeutet „der nächste Raid" (genau das Verhalten des
ausgelieferten WeintAdmin).

- `export_current_signups(raid_id)` gibt jede Anmeldungszeile **so wie sie
  ist** zurück (Klasse/Spec, beide Tagesstatus, `signup_time`); das
  JSON-Feld heißt weiterhin `users`, damit ein bereits ausgeliefertes
  WeintAdmin seine eigenen Backups lesen kann — anders als das
  WCIMPORT-formatierte `/companion/raid-roster`, das nur die aktiven Zusagen
  trägt, nicht den rohen Pro-Tag-Status, den eine Wiederherstellung braucht.
- `restore_signups_into_current_raid()` nutzt **absichtlich nicht**
  `raid_manager.import_raid_snapshot()` (das ersetzt `raid`/`raid_message`
  komplett — richtig bei der Wiederherstellung in eine leere DB, falsch
  hier: der Ziel-Raid wurde gerade frisch erstellt, mit eigener frischer
  Nachricht). Stattdessen schreibt es zeilenweise über
  `user_manager.save_user_signup()` — denselben Weg wie ein Spieler-Klick —
  und lässt Raid-Identität und Nachrichtenbindung unangetastet. Nur Zeilen
  mit `signup_time` werden übernommen (derselbe Filter wie bei
  `import_raid_snapshot()`).

Der Restore-Endpunkt schreibt die DB und ruft danach **synchron**
`cogs.raid.refresh_raid_message()` auf dem Discord-Loop auf
(`run_coroutine_threadsafe` + `future.result(timeout=15)`); das Feld
`message_refreshed` in der Antwort sagt ehrlich, ob die Discord-Embeds den
wiederhergestellten Stand schon zeigen oder noch einen manuellen Anstoß
brauchen — statt `"ok"` zu melden, während die Nachricht still veraltet ist.

## Verwandt, aber nicht Teil dieser Datei

- `/companion/raid-roster` selbst → siehe `wcimport-protocol.md` (der
  WCIMPORT-Inhalt) und `raid-schedule-bridge.md` (die Discord-Präsenzprüfung,
  die auch dieser Endpunkt vor dem Export durchführt: 404, wenn das Sign-up
  in Discord nicht mehr gefunden wird).
- Die Discord-Snapshot-Mechanik (`export_raid_snapshot`/`recover_raid_state`
  im Bot) selbst ist kein Companion-Vertrag — sie ist reine Bot-interne
  Ausfallsicherheit gegen den fehlenden persistenten Speicher des Hosts.
  Dokumentiert in `../../WeintCodex-Bot/docs/systems/raid-persistence.md`.
