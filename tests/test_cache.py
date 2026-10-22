import os
import threading

from resources.lib.common import cache, utils

PATH = "plugin://plugin.program.autowidget/?mode=x"


def _profile(monkeypatch, tmp_path):
    profile = str(tmp_path)
    monkeypatch.setattr(utils, "_addon_data", profile)
    monkeypatch.setattr(cache, "_addon_data", profile)
    monkeypatch.setattr(
        cache, "_playback_history_path", os.path.join(profile, "cache.history")
    )
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


def test_the_sender_thread_gives_up(monkeypatch, tmp_path):
    """The thread that notifies the service may not spin forever."""
    _profile(monkeypatch, tmp_path)

    calls = []
    monkeypatch.setattr(
        cache.utils, "call_jsonrpc", lambda command: calls.append(command) or {}
    )
    monkeypatch.setattr(cache.xbmc, "sleep", lambda ms: None)

    cache.push_cache_queue(PATH, "1")

    for thread in threading.enumerate():
        if (
            thread.name.startswith("Thread-")
            and thread is not threading.current_thread()
        ):
            thread.join(timeout=5)

    assert len(calls) == cache.SEND_RETRIES


def test_the_sender_thread_is_a_daemon(monkeypatch, tmp_path):
    """A thread that is left over may not keep Kodi from shutting down."""
    _profile(monkeypatch, tmp_path)

    created = []
    real_thread = threading.Thread

    def record(*args, **kwargs):
        thread = real_thread(*args, **kwargs)
        created.append(thread)
        return thread

    monkeypatch.setattr(cache.threading, "Thread", record)
    monkeypatch.setattr(cache.utils, "call_jsonrpc", lambda command: {})
    monkeypatch.setattr(cache.xbmc, "sleep", lambda ms: None)

    cache.push_cache_queue(PATH, "1")

    assert created
    assert created[0].daemon is True


def test_the_history_of_a_path_is_capped(monkeypatch, tmp_path):
    """The history describes how often a list changes, a few changes are enough."""
    _profile(monkeypatch, tmp_path)

    for idx in range(cache.MAX_HISTORY_ENTRIES + 10):
        payload = {"result": {"files": [{"label": f"item {idx}", "file": "one.mkv"}]}}
        cache.cache_expiry(PATH, "1", add=payload)

    history = utils.read_json(
        os.path.join(tmp_path, f"{cache.path2hash(PATH)}.history")
    )
    assert len(history["changes"]) == cache.MAX_HISTORY_ENTRIES


def test_the_playback_history_is_capped(monkeypatch, tmp_path):
    _profile(monkeypatch, tmp_path)

    for _ in range(cache.MAX_HISTORY_ENTRIES + 10):
        cache.save_playback_history("movie", 100, PATH)

    history = utils.read_json(os.path.join(tmp_path, "cache.history"))
    assert len(history["plays"]) == cache.MAX_HISTORY_ENTRIES


def test_the_widgets_that_are_gone_are_dropped(monkeypatch, tmp_path):
    """The history of a path only keeps the widgets that still exist."""
    profile = _profile(monkeypatch, tmp_path)

    utils.write_json(os.path.join(profile, "alive.widget"), {"id": "alive"})
    cache.push_cache_queue(PATH, "alive")
    cache.push_cache_queue(PATH, "gone")

    history = utils.read_json(os.path.join(profile, f"{cache.path2hash(PATH)}.history"))
    assert history["widgets"] == ["alive"]


HOUR = 60 * 60


def _write_old_history(profile, path, samples):
    """A history of an older version: a sample on every update."""
    utils.write_json(
        os.path.join(profile, f"{cache.path2hash(path)}.history"),
        {"path": path, "widgets": [], "history": samples},
    )


def test_the_history_of_an_older_version_is_migrated(monkeypatch, tmp_path):
    """A sample was written on every update, the changes are derived from them."""
    profile = _profile(monkeypatch, tmp_path)

    _write_old_history(
        profile,
        PATH,
        [
            (0, "a"),
            (HOUR, "a"),
            (2 * HOUR, "a"),
            (3 * HOUR, "b"),
            (4 * HOUR, "b"),
        ],
    )

    history = cache.read_history(PATH)

    # the change happened somewhere between the two samples
    assert history["changes"] == [(0, "a"), (2.5 * HOUR, "b")]


def test_the_migration_removes_the_samples_of_the_older_version(monkeypatch, tmp_path):
    """The samples are not used any more, they are removed."""
    profile = _profile(monkeypatch, tmp_path)

    _write_old_history(profile, PATH, [(0, "a"), (HOUR, "b")])

    cache.push_cache_queue(PATH, "1")

    history = utils.read_json(os.path.join(profile, f"{cache.path2hash(PATH)}.history"))
    assert "history" not in history
    assert history["changes"] == [[0, "a"], [0.5 * HOUR, "b"]]


def test_only_the_changes_are_written(monkeypatch, tmp_path):
    """A sample on every update would make the file grow forever."""
    profile = _profile(monkeypatch, tmp_path)

    payload = {"result": {"files": [{"label": "one", "file": "one.mkv"}]}}

    for _ in range(5):
        cache.cache_expiry(PATH, "1", add=payload)

    history = utils.read_json(os.path.join(profile, f"{cache.path2hash(PATH)}.history"))
    # the content never changed, so there is one change only
    assert len(history["changes"]) == 1


def test_a_change_is_written_when_the_content_changes(monkeypatch, tmp_path):
    profile = _profile(monkeypatch, tmp_path)

    cache.cache_expiry(
        PATH, "1", add={"result": {"files": [{"label": "one", "file": "one.mkv"}]}}
    )
    cache.cache_expiry(
        PATH, "1", add={"result": {"files": [{"label": "two", "file": "two.mkv"}]}}
    )

    history = utils.read_json(os.path.join(profile, f"{cache.path2hash(PATH)}.history"))
    assert len(history["changes"]) == 2
    assert history["changes"][0][1] != history["changes"][1][1]


def test_the_prediction_uses_the_time_between_the_changes():
    """A list that changes every 12 hours may be cached for 6 hours."""
    changes = [(idx * 12 * HOUR, f"hash-{idx}") for idx in range(10)]

    lifetime = cache.predict_update_frequency(changes)

    assert lifetime == 6 * HOUR


def test_the_prediction_of_a_list_that_never_changes():
    """A list that never changed is the same since the first change."""
    changes = [(0, "a")]

    lifetime = cache.predict_update_frequency(changes, now=24 * HOUR)

    assert lifetime == 12 * HOUR


def test_the_prediction_of_a_list_that_never_changed_is_bounded():
    """A list that starts to change after a year of silence is too old."""
    changes = [(0, "a")]

    lifetime = cache.predict_update_frequency(changes, now=365 * 24 * HOUR)

    assert lifetime == cache.MAX_CURRENT_STREAK / 2


def test_the_prediction_without_a_history():
    assert cache.predict_update_frequency([]) == cache.DEFAULT_CACHE_TIME


def test_the_playback_that_changed_the_content_is_counted():
    changes = [(HOUR, "b")]

    prob = cache.chance_playback_updates_widget(
        {"changes": changes, "path": PATH}, [(30 * 60, "movie")]
    )

    # the content changed within the hour after the playback
    assert prob > 0.5


def test_the_playback_that_changed_nothing_is_counted():
    changes = [(10 * HOUR, "b")]

    prob = cache.chance_playback_updates_widget(
        {"changes": changes, "path": PATH}, [(30 * 60, "movie")]
    )

    # the content did not change after the playback
    assert prob < 0.5


def test_the_lifetime_is_at_least_half_the_refresh_interval(monkeypatch):
    """A shorter lifetime would make the reader refresh what the service
    refreshes anyway."""
    monkeypatch.setattr(cache.settings, "get_setting_float", lambda setting: 2)

    # a list that changes every 10 minutes
    changes = [(idx * 600, "hash-{idx}") for idx in range(10)]

    lifetime = cache.cache_lifetime(changes)

    assert lifetime == 1 * HOUR


def test_the_lifetime_is_longer_when_the_list_changes_slowly(monkeypatch):
    monkeypatch.setattr(cache.settings, "get_setting_float", lambda setting: 2)

    changes = [(idx * 12 * HOUR, "hash-{idx}") for idx in range(10)]

    lifetime = cache.cache_lifetime(changes)

    assert lifetime == 6 * HOUR


def test_the_lifetime_without_a_refresh_interval(monkeypatch):
    """Without the setting of the service there is no minimum."""
    monkeypatch.setattr(cache.settings, "get_setting_float", lambda setting: 0)

    changes = [(idx * 600, "hash-{idx}") for idx in range(10)]

    lifetime = cache.cache_lifetime(changes)

    assert lifetime == 300
