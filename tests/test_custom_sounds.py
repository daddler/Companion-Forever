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
