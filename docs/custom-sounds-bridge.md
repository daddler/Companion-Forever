# Eigene Töne für „Raus da!“: Vertrag zwischen Companion und Addon

Der Spieler wählt in der Companion (Seite **Töne**, `gui/pages/sounds.py`)
bis zu fünf eigene Audiodateien; WeintCodex bietet sie im Komfort unter
*Raus da! → Ton* ganz oben an. Der Bot ist nicht beteiligt, nichts geht
ins Netz.

| Seite | Datei | Ab Version |
|-------|-------|------------|
| Companion, schreibend | `core/custom_sounds.py` | WeintCompanion 5.3.0 |
| Addon, lesend | `ui/firealarm.lua` (`FA.MergeCustom`, `FA.FileOf`) | WeintCodex 6.146.0.0 |

## Ablageort: ein eigenes Addon, nie `WeintCodex/`

```
Interface/AddOns/WeintCodex_Sounds/
    WeintCodex_Sounds.toc   ## Interface wie im installierten WeintCodex.toc
    sounds.lua              WeintCodex_CustomSounds = { … }
    sounds.json             Ablage der Companion (Name, Herkunft)
    eigen1.ogg … eigen5.ogg
```

Der Ordner `WeintCodex` wird bei jedem Update vollständig ersetzt
(`core/installer.py`) – Töne darin wären nach dem nächsten Update weg,
ohne dass es jemand merkt. Fehlt `WeintCodex.toc`, bleibt die
`## Interface`-Zeile weg statt geraten.

## Format

```lua
WeintCodex_CustomSounds = {
    { key = "eigen1", file = "eigen1.ogg", text = "Gong der Gilde" },
}
```

- `key` ist **fest** `eigen1` … `eigen5`. Das Addon speichert die Wahl
  des Spielers unter diesem Schlüssel: ein ersetzter Ton bleibt gewählt,
  ein entfernter fällt auf den Standard („raus“) zurück.
- `file` muss `<key>.ogg` sein (Ogg Vorbis). Das Addon übergeht jeden
  Eintrag, der nicht `^eigen%d+$` / `^[%w_]+%.ogg$` entspricht – kein
  Pfad aus der Datei wird je zusammengesetzt, außer unter
  `Interface\AddOns\WeintCodex_Sounds\`.
- `text` ist der Name, wie ihn der Spieler vergeben hat (≤ 40 Zeichen,
  ohne Anführungszeichen und Backslash).

## Regeln

- **Gelesen wird beim Gebrauch, nie beim Laden.** `WeintCodex_Sounds`
  lädt nach `WeintCodex`; `FA.MergeCustom()` läuft vor der Liste, der
  Probe und jedem Ton.
- **Neue Dateien kennt WoW erst nach einem Neustart des Spiels**, nicht
  nach `/reload`. Beide Seiten sagen das dem Spieler.
- **Umwandeln nur mit ffmpeg.** Gefunden (`PATH`): jede Eingabe wird zu
  mono Ogg Vorbis, gekürzt auf 4 s mit 0,15 s Ausblenden. Ohne ffmpeg wird
  nur eine echte `.ogg` (Kopf `OggS`, ≤ 2 MB) kopiert; alles andere wird
  mit Grund abgelehnt, nie halb übernommen.
