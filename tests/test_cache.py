import os

from resources.lib.common import cache, utils

PATH = "plugin://plugin.program.autowidget/?mode=x"


def _profile(monkeypatch, tmp_path):
    profile = str(tmp_path)
    monkeypatch.setattr(utils, "_addon_data", profile)
    monkeypatch.setattr(cache, "_addon_data", profile)
    return profile


def test_path2hash_is_stable():
    # The hash is used as the name of the cache files, it must not change
    # between releases or all cached data would be lost.
    assert cache.path2hash(PATH) == "2061c2d58b9b7eb9be4c41f6c6c76ef929e9df15"
    assert cache.path2hash("a") == cache.path2hash("a")
    assert cache.path2hash("a") != cache.path2hash("b")


def test_path2hash_of_none():
    assert cache.path2hash(None) is None


def test_widgets_for_path_tracks_the_widgets(monkeypatch, tmp_path):
    profile = _profile(monkeypatch, tmp_path)

    assert cache.widgets_for_path(PATH) == set()

    utils.write_json(
        os.path.join(profile, f"{cache.path2hash(PATH)}.history"),
        {"widgets": ["1", "2"]},
    )
    assert cache.widgets_for_path(PATH) == {"1", "2"}


def test_cache_expiry_writes_and_reads_back(monkeypatch, tmp_path):
    profile = _profile(monkeypatch, tmp_path)

    payload = {"result": {"files": [{"label": "one", "file": "one.mkv"}]}}
    expiry, contents, changed = cache.cache_expiry(PATH, "1", add=payload)
    assert changed is True
    assert contents == payload

    cache_path = os.path.join(profile, f"{cache.path2hash(PATH)}.cache")
    assert utils.read_json(cache_path) == payload

    expiry, contents, changed = cache.cache_expiry(PATH, "1")
    assert contents == payload
    assert expiry > 0


def test_cache_expiry_does_not_cache_errors(monkeypatch, tmp_path):
    profile = _profile(monkeypatch, tmp_path)

    expiry, contents, changed = cache.cache_expiry(
        PATH, "1", add={"error": {"code": -1}}
    )
    assert contents is None

    cache_path = os.path.join(profile, f"{cache.path2hash(PATH)}.cache")
    assert not os.path.exists(cache_path)


def test_cache_expiry_holds_the_content_while_it_is_updated(monkeypatch, tmp_path):
    _profile(monkeypatch, tmp_path)

    expiry, contents, changed = cache.cache_expiry(PATH, "1")
    # Nothing cached yet, but the user gets a placeholder to look at
    assert contents is not None
    assert contents["result"]["files"][0]["label"]
