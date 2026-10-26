# Werbevideo WeintCompanion

Werbevideo für das Weint-Ökosystem (Codex, Companion, Bot) mit 2:01 Minuten in 1920×1080, Sprecher, Untertiteln und Musik.
Die gerenderte Fassung v3 liegt nicht im Repo, weil sie zu groß ist. Sie lässt sich aus diesem Ordner jederzeit neu bauen.

## Aufbau

| Datei | Zweck |
|---|---|
| `tts/script.json` | Sprechertext: 9 Szenen mit 28 Sätzen. Die Sätze werden auch als Untertitel gezeigt. |
| `tts/voice.py` | Sprachausgabe mit Piper (`de_DE-thorsten-high`). Die Aussprache wird auf IPA-Ebene korrigiert (`IPA_FIX`, z. B. Bot → [bɔt]), dazu kommt die Whisper-Prüfung (`hear`). |
| `tts/build_voice.py` | Erzeugt jeden Satz bis zu 8×, Whisper hört mit und ohne Musik ab, die beste Fassung wird genommen. Legt die Szenen auf ganze Takte (110 BPM). Ergebnis: `voice.wav`, `timeline.json`, `timeline.js`. |
| `music2.py` | Musik aus `timeline.json`: a-Moll, Flächen, Arpeggio, Bass, Drums, Lead, Riser/Impacts an den Szenenwechseln. Ergebnis: `music2.wav`. |
| `mix.sh` | Stimme bearbeiten, Musik unter der Stimme absenken (Ducking), Lautheit auf −14 LUFS. Ergebnis: `mix.wav`. |
| `tts/check_mix.py` | Whisper prüft jeden Satz im fertigen Mix. |
| `index.html` | Alle Szenen als HTML/CSS. Zeitleiste aus `timeline.js`, gesteuert über `setTime(t)`. |
| `render.js` | Rendert mit Playwright Bild für Bild nach `video_noaudio.mp4` (30 fps, ~15 min). |
| `preview.js` | Einzelbilder: `node preview.js "$PWD" 10 40 90` |

## Bauen

```bash
pip install piper-tts sherpa-onnx scipy soundfile numpy
# Stimme:  github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-de_DE-thorsten-high.tar.bz2
# Whisper: github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-turbo.tar.bz2
# beide nach tts/ entpacken
cd promo/werbevideo
python3 tts/build_voice.py "$PWD"      # braucht ein vorhandenes music2.wav als Prüfbett; beim ersten Mal erst music2.py
python3 music2.py timeline.json music2.wav
./mix.sh && python3 tts/check_mix.py
node render.js "$PWD"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 video_noaudio.mp4)
ffmpeg -i video_noaudio.mp4 -i mix.wav -filter_complex "[1:a]atrim=0:$D,afade=t=out:st=$(python3 -c "print($D-2.2)"):d=2.2[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -movflags +faststart WeintCompanion_Werbevideo.mp4
```

## Stand und nächster Schritt

- v3 ist fertig und vom Besitzer abgenommen. Einziger offener Punkt: Die Stimme klingt zu sehr nach Computer.
- Als Nächstes wird die Stimme durch **ElevenLabs** ersetzt (Gratis-Plan, „Multilingual v2“, deutsche Stimme). Der Gratis-Plan verlangt die Nennung „Stimme: ElevenLabs“ im Abspann oder in der Beschreibung.
  - Dafür ersetzt `say()` in `tts/voice.py` die Piper-Ausgabe durch einen Aufruf von `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`. Der Header ist `xi-api-key`, nicht `Authorization`. Der Schlüssel kommt aus der Umgebungsvariablen `ELEVENLABS_API_KEY`.
  - Die Lautschrift-Korrekturen (`SAY`, `IPA_FIX`) sind auf Piper zugeschnitten und bei ElevenLabs vermutlich unnötig. Ob sie gebraucht werden, entscheidet die Whisper-Prüfung.
  - Text, Zeitleiste, Szenen, Musik und Mix bleiben unverändert.
- Das Bildmaterial ist nachgebaut, es sind keine Screenshots aus dem Spiel. Die Beispieldaten (Spielernamen, „14 Spieler gemeldet“) sind erfunden. Taktiken oder Inhalte aus Mists of Pandaria kommen nicht vor.
