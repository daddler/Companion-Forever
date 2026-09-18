"""
Die Spielversionstabelle (`core/wow_clients.py`) und was daran hängt:
die Suche auf der Platte (`addon/finder.py`) und die Konfiguration
(`core/config.py`).

Seit 5.0 steht dort **eine** Spielversion: Forever. Diese Datei prüft
deshalb zwei Dinge, die sich auf den ersten Blick widersprechen und es
nicht tun:

1. dass die Tabelle eine Tabelle bleibt - eine zweite Version ist ein
   Eintrag und kein Umbau, und die Wege dorthin (eigener Pfad je
   Version, Ausschluss fremder Ordner) funktionieren mit einem Eintrag
   genauso wie mit zweien;
2. dass die Konfiguration eines Nutzers, der von der alten Companion
   herüberkommt, **nicht** stillschweigend als Forever-Einrichtung
   gelesen wird. Sein `mop_classic` fällt auf Forever zurück, sein
   MoP-Ordner aber wird nicht zum Forever-Ordner.
"""

import json

from addon.finder import WoWFinder
from core.config import Config
from core.paths import Paths
from core.wow_clients import (
    CLIENTS,
    DEFAULT_CLIENT_ID,
    FOREVER,
    client,
    default_client,
    foreign_flavor_folders,
    released_clients,
)


def _make_installation(base, name):

    folder = base / name

    (folder / "Interface" / "AddOns").mkdir(parents=True)

    (folder / "WTF").mkdir(parents=True)

    return folder


# --------------------------------------------------
# Die Tabelle
# --------------------------------------------------


def test_every_client_has_a_unique_id():

    ids = [entry.id for entry in CLIENTS]

    assert len(ids) == len(set(ids))


def test_an_unknown_id_falls_back_instead_of_raising():
    """
    Der Wert kommt aus der config.json und damit aus einer Datei, die
    ein Nutzer von Hand ändern kann - ein Tippfehler darf den Start
    nicht verhindern.
    """

    assert client("gibt-es-nicht") is default_client()

    assert client(None) is default_client()

    assert default_client().id == DEFAULT_CLIENT_ID


def test_the_retired_mop_id_falls_back_to_forever():
    """
    Der Weg von der alten Companion herüber. `mop_classic` steht in
    jeder bestehenden Konfiguration; dass es diese Spielversion hier
    nicht mehr gibt, ist kein Fehler des Nutzers und darf sich nicht
    wie einer anfühlen.
    """

    assert client("mop_classic") is FOREVER


def test_forever_knows_its_level_cap_but_only_guesses_its_folder():
    """
    Die Stufengrenze ist bestätigt, der Ordnername nicht - und die
    Vermutung darf hier stehen, weil ein Fehlgriff folgenlos ist:
    dann sucht `addon/finder.py` über die Kennzeichen weiter.
    """

    assert FOREVER.max_level == 60

    assert FOREVER.folder_known


def test_nothing_is_offered_in_the_setup_before_release():
    """
    Solange Forever nicht erschienen ist, gibt es nichts zu wählen -
    und die Einrichtung fragt deshalb nicht, sondern nimmt die Vorgabe.
    """

    assert released_clients() == ()

    assert not FOREVER.released


def test_a_clients_own_folder_name_is_not_foreign_to_itself():

    assert "_forever_" not in foreign_flavor_folders(FOREVER)

    assert "_classic_" in foreign_flavor_folders(FOREVER)


def test_the_classic_beta_folder_stays_foreign():
    """
    Die Forever-Beta lief darin - aber jede Classic-Beta tut das. Eine
    liegengebliebene Installation daraus als Forever auszugeben wäre
    genau die stille Verwechslung, gegen die die Liste da ist.
    """

    assert "_classic_beta_" in foreign_flavor_folders(FOREVER)


# --------------------------------------------------
# Suche auf der Platte
# --------------------------------------------------


def test_the_finder_looks_for_the_clients_own_folder(tmp_path):

    root = tmp_path / "World of Warcraft"

    forever = _make_installation(root, "_forever_")

    _make_installation(root, "_retail_")

    finder = WoWFinder(FOREVER)

    finder.search_roots = [tmp_path]

    assert finder.find() == forever


def test_the_finder_ignores_other_flavours(tmp_path):
    """
    Ohne den Ausschluss fände eine Suche nach Forever `_retail_` und
    gäbe es als Forever aus.
    """

    root = tmp_path / "World of Warcraft"

    _make_installation(root, "_retail_")

    _make_installation(root, "_classic_era_")

    finder = WoWFinder(FOREVER)

    finder.search_roots = [tmp_path]

    assert finder.find() is None


def test_the_finder_does_not_accept_a_stray_folder(tmp_path):
    """
    Bei bekanntem Ordnernamen bleibt die Suche eng: ein Ordner, der
    zufällig Interface/ und WTF/ enthält, ist kein Treffer.
    """

    _make_installation(tmp_path, "irgendein-ordner")

    finder = WoWFinder(FOREVER)

    finder.search_roots = [tmp_path]

    assert finder.find() is None


# --------------------------------------------------
# Konfiguration
# --------------------------------------------------


def test_the_mop_path_does_not_become_the_forever_path(tmp_path, monkeypatch):
    """
    Der wichtigste Test dieser Datei.

    Wer von der alten Companion herüberkommt, bringt `classic_path`
    und `wow_paths["mop_classic"]` mit - den Ordner seiner
    MoP-Installation. Würde der als Forever-Pfad gelesen, installierte
    diese App das Addon in die falsche Spielversion, und zwar ohne
    Rückfrage. Er muss seinen Ordner einmal wählen; das ist die
    zumutbare Hälfte der beiden Möglichkeiten.
    """

    monkeypatch.setattr(Paths, "config", staticmethod(lambda: tmp_path))

    installation = _make_installation(tmp_path, "_classic_")

    (tmp_path / "config.json").write_text(
        json.dumps(
            {
                "wow_client": "mop_classic",
                "classic_path": str(installation),
                "wow_paths": {"mop_classic": str(installation)},
            }
        ),
        encoding="utf-8",
    )

    config = Config()

    assert config.get_wow_client().id == FOREVER.id

    assert config.get_wow_path() is None


def test_the_old_keys_are_left_alone(tmp_path, monkeypatch):
    """
    Sie werden nicht gelesen - gelöscht werden sie aber auch nicht.
    Es ist dieselbe Datei, die eine ältere Companion-Fassung liest,
    falls jemand zurückgeht.
    """

    monkeypatch.setattr(Paths, "config", staticmethod(lambda: tmp_path))

    installation = _make_installation(tmp_path, "_classic_")

    (tmp_path / "config.json").write_text(
        json.dumps(
            {
                "classic_path": str(installation),
                "wow_paths": {"mop_classic": str(installation)},
            }
        ),
        encoding="utf-8",
    )

    config = Config()

    config.set_wow_path(_make_installation(tmp_path, "_forever_"))

    stored = json.loads(
        (tmp_path / "config.json").read_text(encoding="utf-8")
    )

    assert stored["classic_path"] == str(installation)

    assert stored["wow_paths"]["mop_classic"] == str(installation)


def test_the_path_is_stored_per_client(tmp_path, monkeypatch):
    """
    Auch mit einer einzigen Spielversion: der Pfad hängt an ihrer
    Kennung und nicht an "dem Pfad". Das ist die Naht, an der die
    nächste Version dazukommt.
    """

    monkeypatch.setattr(Paths, "config", staticmethod(lambda: tmp_path))

    forever = _make_installation(tmp_path, "_forever_")

    config = Config()

    config.set_wow_path(forever)

    assert config.data["wow_paths"][FOREVER.id] == str(forever)

    assert config.get_wow_path() == forever

    assert config.get_wow_path(FOREVER.id) == forever


def test_a_path_that_disappeared_counts_as_none(tmp_path, monkeypatch):

    monkeypatch.setattr(Paths, "config", staticmethod(lambda: tmp_path))

    config = Config()

    config.set_wow_path(tmp_path / "abgezogene-platte")

    assert config.get_wow_path() is None
