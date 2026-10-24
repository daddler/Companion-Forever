"""
"Angezeigt verbunden, aber nicht angemeldet": die Verknüpfung hat
fünf Zustände, und nur `ok` heißt verbunden (core/discord_account.py).
"""

import pytest

from core import discord_account as da
from core.discord_account import (
    LINK_NONE,
    LINK_OK,
    LINK_REJECTED,
    LINK_UNREACHABLE,
    LINK_UNVERIFIED,
    DiscordAccountStore,
    link_state,
)


TOKEN = {"username": "Weint", "companion_token": "abc"}


def test_without_a_token_nothing_is_linked():

    assert link_state(None, LINK_OK) == LINK_NONE
    assert link_state({"username": "Weint"}, LINK_OK) == LINK_NONE


def test_a_stored_token_alone_is_not_a_confirmed_login():

    assert link_state(TOKEN, None) == LINK_UNVERIFIED


@pytest.mark.parametrize("verdict", [LINK_OK, LINK_REJECTED, LINK_UNREACHABLE])
def test_the_bots_verdict_is_passed_through(verdict):

    assert link_state(TOKEN, verdict) == verdict


@pytest.fixture
def store(tmp_path, monkeypatch):

    monkeypatch.setattr(da.Paths, "config", staticmethod(lambda: tmp_path))
    da.set_logger(None)

    s = DiscordAccountStore()
    s.clear()

    yield s

    s.clear()


def test_a_fresh_login_counts_as_confirmed(store):

    store.save(dict(TOKEN))

    assert store.state() == LINK_OK


def test_a_rejection_shows_before_the_unlink(store):

    store.save(dict(TOKEN))
    store.note_auth_rejected()

    assert store.state() == LINK_REJECTED


def test_silence_does_not_lift_a_rejection(store):

    store.save(dict(TOKEN))
    store.note_auth_rejected()
    store.note_unreachable()

    assert store.state() == LINK_REJECTED


def test_an_unreachable_bot_is_not_a_login(store):

    store.save(dict(TOKEN))
    store.note_unreachable()

    assert store.state() == LINK_UNREACHABLE

    store.note_auth_ok()

    assert store.state() == LINK_OK


def test_clearing_forgets_the_verdict(store):

    store.save(dict(TOKEN))
    store.clear()

    assert store.state() == LINK_NONE
