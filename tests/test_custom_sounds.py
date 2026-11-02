"""
Eigene Töne für "Raus da!" (core/custom_sounds.py,
docs/custom-sounds-bridge.md).
"""

import shutil

import pytest

from core import custom_sounds as cs


OGG = b"OggS" + b"\0" * 60


@pytest.fixture
def addons(tmp_path):

    root = tmp_path / "Interface" / "AddOns"
    (root / "WeintCodex").mkdir(parents=True)
    (root / "WeintCodex" / "WeintCodex.toc").write_text(
        "## Interface: 120000, 16001\n## Title: X\n", encoding="utf-8"
    )
    return root


def _ogg(tmp_path, name="gong.ogg"):

    path = tmp_path / name
    path.write_bytes(OGG)
    return path


def test_without_a_wow_folder_there_are_no_sounds():

    assert cs.load(None) == []


def test_an_ogg_is_taken_without_ffmpeg(addons, tmp_path):

    sound = cs.add(addons, _ogg(tmp_path), ffmpeg="")

    assert sound.key == "eigen1" and sound.name == "gong"
    base = addons / cs.FOLDER_NAME
    assert (base / "eigen1.ogg").read_bytes() == OGG
    lua = (base / cs.LUA_FILE).read_text(encoding="utf-8")
    assert 'key = "eigen1", file = "eigen1.ogg", text = "gong"' in lua
    toc = (base / cs.TOC_FILE).read_text(encoding="utf-8")
    assert toc.startswith("## Interface: 120000, 16001\n")
    assert cs.LUA_FILE in toc


def test_the_sounds_never_go_into_the_addon_folder(addons, tmp_path):

    cs.add(addons, _ogg(tmp_path), ffmpeg="")

    assert not any((addons / "WeintCodex").glob("*.ogg"))


def test_a_fake_ogg_is_refused(addons, tmp_path):

    fake = tmp_path / "x.ogg"
    fake.write_bytes(b"ID3 nope")

    with pytest.raises(cs.SoundError, match="keine Ogg"):
        cs.add(addons, fake, ffmpeg="")


def test_mp3_without_ffmpeg_says_what_is_missing(addons, tmp_path):

    mp3 = tmp_path / "a.mp3"
    mp3.write_bytes(b"ID3")

    with pytest.raises(cs.SoundError, match="ffmpeg"):
        cs.add(addons, mp3, ffmpeg="")

    assert cs.load(addons) == []


def test_slots_fill_and_run_out(addons, tmp_path):

    for i in range(cs.SLOTS):
        assert cs.add(addons, _ogg(tmp_path), ffmpeg="").key == f"eigen{i + 1}"

    with pytest.raises(cs.SoundError, match="belegt"):
        cs.add(addons, _ogg(tmp_path), ffmpeg="")


def test_replace_rename_remove(addons, tmp_path):

    cs.add(addons, _ogg(tmp_path), ffmpeg="")
    cs.add(addons, _ogg(tmp_path, "b.ogg"), key="eigen1", ffmpeg="")

    assert [s.source for s in cs.load(addons)] == ["b.ogg"]

    cs.rename(addons, "eigen1", 'Böser "Gong"\\')
    assert cs.load(addons)[0].name == "Böser Gong"

    cs.remove(addons, "eigen1")
    assert cs.load(addons) == []
    assert not (addons / cs.FOLDER_NAME / "eigen1.ogg").exists()


def test_lua_strings_are_escaped():

    lua = cs.render_lua([cs.CustomSound("eigen1", "eigen1.ogg", 'a"b\\c')])

    assert 'text = "a\\"b\\\\c"' in lua


def test_a_missing_file_is_not_listed(addons, tmp_path):

    cs.add(addons, _ogg(tmp_path), ffmpeg="")
    (addons / cs.FOLDER_NAME / "eigen1.ogg").unlink()

    assert cs.load(addons) == []


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg fehlt")
def test_ffmpeg_turns_a_long_wav_into_a_short_ogg(addons, tmp_path):

    import math
    import struct
    import wave

    wav = tmp_path / "lang.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(22050)
        w.writeframes(b"".join(
            struct.pack("<h", int(8000 * math.sin(i / 10)))
            for i in range(22050 * 10)
        ))

    sound = cs.add(addons, wav)

    out = addons / cs.FOLDER_NAME / sound.file
    assert out.read_bytes()[:4] == b"OggS"
    assert out.stat().st_size < wav.stat().st_size / 4


def test_without_libvorbis_the_builtin_encoder_takes_over(addons, tmp_path):
    """
    Ein ffmpeg-Bau ohne libvorbis darf den Import nicht scheitern
    lassen: der zweite Versuch nimmt den eingebauten Kodierer.
    """

    fake = tmp_path / "ffmpeg"
    fake.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "if 'libvorbis' in sys.argv: sys.exit(1)\n"
        "open(sys.argv[-1], 'wb').write(b'OggS' + bytes(20))\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)

    src = tmp_path / "a.mp3"
    src.write_bytes(b"ID3")

    sound = cs.add(addons, src, ffmpeg=str(fake))

    assert (addons / cs.FOLDER_NAME / sound.file).read_bytes()[:4] == b"OggS"


# --------------------------------------------------
# Schneiden (1.4.0)
# --------------------------------------------------

FFMPEG = cs.ffmpeg_path()


def test_clip_window_keeps_the_choice_inside_the_rules():

    assert cs.clip_window(2.0, 5.0) == (2.0, 3.0)
    # Länger als MAX_SECONDS: gekürzt, nie länger.
    assert cs.clip_window(1.0, 20.0) == (1.0, cs.MAX_SECONDS)
    # Ohne Ende: ab Start die erlaubte Länge, nicht über das Dateiende.
    assert cs.clip_window(1.0, None, 3.0) == (1.0, 2.0)
    with pytest.raises(cs.SoundError, match="zu kurz"):
        cs.clip_window(2.0, 2.05)
    with pytest.raises(cs.SoundError, match="hinter dem Ende"):
        cs.clip_window(9.0, 10.0, 8.0)


def test_cutting_without_ffmpeg_is_refused(addons, tmp_path):

    with pytest.raises(cs.SoundError, match="Schneiden"):
        cs.add(addons, _ogg(tmp_path), ffmpeg="", start=1.0, end=2.0)


def _tone_in_silence(path):
    """3 s Stille, 2 s Ton, 3 s Stille - als WAV, ohne ffmpeg gebaut."""

    import math
    import struct
    import wave

    rate = 8000
    frames = []
    for i in range(rate * 8):
        on = 3 * rate <= i < 5 * rate
        frames.append(struct.pack("<h", int(12000 * math.sin(i / 3)) if on else 0))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(frames))
    return path


@pytest.mark.skipif(not FFMPEG, reason="ffmpeg fehlt")
def test_duration_and_waveform_show_where_the_sound_is(tmp_path):

    src = _tone_in_silence(tmp_path / "ton.wav")

    assert abs(cs.probe_duration(src, FFMPEG) - 8.0) < 0.1

    peaks = cs.waveform(src, FFMPEG, buckets=16)

    assert len(peaks) == 16
    loud = [i for i, p in enumerate(peaks) if p > 0.5]
    assert loud and loud[0] >= 5 and loud[-1] <= 10


@pytest.mark.skipif(not FFMPEG, reason="ffmpeg fehlt")
def test_saving_takes_exactly_the_chosen_cut(addons, tmp_path):

    src = _tone_in_silence(tmp_path / "ton.wav")

    sound = cs.add(addons, src, ffmpeg=FFMPEG, start=3.0, end=5.0)

    out = addons / cs.FOLDER_NAME / sound.file
    assert out.read_bytes()[:4] == b"OggS"
    assert abs(cs.probe_duration(out, FFMPEG) - 2.0) < 0.1
    # Der Ausschnitt ist der Ton, nicht die Stille davor.
    assert max(cs.waveform(out, FFMPEG, buckets=8)) > 0


@pytest.mark.skipif(not FFMPEG, reason="ffmpeg fehlt")
def test_cover_art_of_an_mp3_does_not_end_up_as_video(addons, tmp_path):
    """
    Eine mp3 mit Titelbild wurde bis 1.4.1 zu einer .ogg mit Theora-Video -
    und die spielt das Spiel stumm ab. Nur die Tonspur darf hinein.
    """

    import subprocess

    wav = _tone_in_silence(tmp_path / "ton.wav")
    cover = tmp_path / "cover.png"
    mp3 = tmp_path / "meme.mp3"
    run = lambda *a: subprocess.run([FFMPEG, "-v", "error", "-y", *a], check=True)
    run("-f", "lavfi", "-i", "color=red:s=64x64:d=1", "-frames:v", "1", str(cover))
    run("-i", str(wav), "-i", str(cover), "-map", "0", "-map", "1",
        "-c:a", "libmp3lame", "-c:v", "mjpeg", "-disposition:v", "attached_pic", str(mp3))

    sound = cs.add(addons, mp3, ffmpeg=FFMPEG, start=3.0, end=5.0)

    probe = subprocess.run([FFMPEG, "-hide_banner", "-i", str(addons / cs.FOLDER_NAME / sound.file)],
                           capture_output=True, text=True).stderr
    assert "Audio: vorbis" in probe
    assert "Video:" not in probe


def test_unknown_duration_is_unknown_not_zero(tmp_path):

    junk = tmp_path / "kaputt.mp3"
    junk.write_bytes(b"nichts")
    assert cs.probe_duration(junk, FFMPEG or "/nicht/da") is None


def test_length_goes_to_the_addon_so_a_long_sound_is_not_restarted(addons, tmp_path):

    sound = cs.CustomSound("eigen1", "eigen1.ogg", "Meme", "x.mp3", 5.39)
    lua = cs.render_lua([sound])
    assert "len = 5.39" in lua
    # Unbekannte Länge: kein Feld, nicht 0.
    assert "len" not in cs.render_lua([cs.CustomSound("eigen1", "eigen1.ogg", "Gong")])
    assert cs._length(True) is None and cs._length(0) is None and cs._length("5") is None
    assert cs._length(5.391) == 5.39


@pytest.mark.skipif(not FFMPEG, reason="ffmpeg fehlt")
def test_cut_length_is_measured_and_kept_through_rename(addons, tmp_path):

    src = _tone_in_silence(tmp_path / "ton.wav")
    cs.add(addons, src, ffmpeg=FFMPEG, start=1.94, end=7.33)
    sound = cs.load(addons)[0]
    assert abs(sound.length - 5.39) < 0.1
    cs.rename(addons, "eigen1", "Rose")
    assert cs.load(addons)[0].length == sound.length
    lua = (addons / cs.FOLDER_NAME / cs.LUA_FILE).read_text(encoding="utf-8")
    assert "len = " in lua
