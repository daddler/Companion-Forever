"""
macOS-Unterstützung: Datenordner, Autostart, Battle.net, WoW-Suche.

Läuft auf jedem System - `platform.system()` wird vorgetäuscht.
"""

from pathlib import Path
import plistlib

import pytest


@pytest.fixture
def macos(monkeypatch, tmp_path):

    import platform

    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    return tmp_path


def test_data_folder_is_application_support(macos):

    from core.paths import Paths

    assert Paths.base() == (
        macos / "Library" / "Application Support" / "WeintCompanion"
    )


def test_existing_legacy_folder_is_kept(macos):

    from core.paths import Paths

    (macos / ".weintcompanion").mkdir()

    assert Paths.base() == macos / ".weintcompanion"


def test_autostart_writes_and_removes_launch_agent(macos):

    from core.autostart import Autostart, MACOS_AGENT_LABEL

    assert Autostart.is_supported()
    assert Autostart.set_enabled(True)
    assert Autostart.is_enabled()

    plist = macos / "Library" / "LaunchAgents" / f"{MACOS_AGENT_LABEL}.plist"

    with open(plist, "rb") as file:
        data = plistlib.load(file)

    assert data["Label"] == MACOS_AGENT_LABEL
    assert data["RunAtLoad"] is True

    assert Autostart.set_enabled(False)
    assert not plist.exists()


def test_battlenet_app_found_next_to_wow(tmp_path):

    from core.battlenet_launcher import BattleNetLauncher

    apps = tmp_path / "Applications"
    (apps / "Battle.net.app").mkdir(parents=True)
    wow = apps / "World of Warcraft" / "_forever_"
    wow.mkdir(parents=True)

    launcher = BattleNetLauncher(config=None)

    assert launcher.find_macos_app(wow) == apps / "Battle.net.app"


def test_finder_does_not_enter_app_bundles(tmp_path):

    from addon.finder import WoWFinder

    hidden = tmp_path / "Xcode.app" / "World of Warcraft" / "_forever_"

    for part in ("Interface/AddOns", "WTF"):
        (hidden / part).mkdir(parents=True)

    finder = WoWFinder()

    assert finder._search(tmp_path, set()) is None


def test_github_picks_dmg_on_macos(monkeypatch):

    import platform

    from core.github_updater import GitHubUpdater

    monkeypatch.setattr(platform, "system", lambda: "Darwin")

    updater = GitHubUpdater(owner="daddler", repo="Companion-Forever")

    assert updater._wanted_asset() == ".dmg"
