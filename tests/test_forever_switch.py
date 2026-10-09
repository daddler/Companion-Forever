from core.forever_switch import SEEN_KEY, came_from_old_companion, needs_notice


def test_fresh_forever_config_gets_no_notice():

    assert not needs_notice({"wow_client": "forever", "wow_paths": {}})


def test_config_from_4_0_is_recognised_by_classic_path_even_if_empty():

    # 4.0 kannte weder `wow_client` noch `wow_paths` - nur `classic_path`.
    assert came_from_old_companion({"classic_path": ""})


def test_config_from_4_1_is_recognised():

    assert came_from_old_companion(
        {"wow_client": "mop_classic", "wow_paths": {"mop_classic": "C:/WoW"}}
    )


def test_notice_only_once():

    data = {"classic_path": "C:/WoW", SEEN_KEY: True}

    assert not needs_notice(data)


def test_broken_wow_paths_does_not_crash():

    assert not came_from_old_companion({"wow_paths": "C:/WoW"})
