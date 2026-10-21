import os

from resources.lib.common import cache
from resources.lib.common import utils

PATH = "plugin://plugin.program.autowidget/?mode=x"
OTHER_PATH = "plugin://plugin.program.autowidget/?mode=y"


def _profile(monkeypatch, tmp_path):
    profile = str(tmp_path)
    monkeypatch.setattr(utils, "_addon_data", profile)
    monkeypatch.setattr(cache, "_addon_data", profile)
    return profile


def test_a_path_is_queued_with_the_widget_that_asked_for_it(monkeypatch, tmp_path):
    """The service needs the widget id to update the widget after a refresh."""
    _profile(monkeypatch, tmp_path)

    queued = []
    monkeypatch.setattr(
        cache, "push_cache_queue", lambda path, widget_id=None: queued.append((path, widget_id))
    )

    cache.cache_expiry(PATH, "widget-id")

    assert queued == [(PATH, "widget-id")]


def test_cache_and_update_survives_a_missing_widget_id(monkeypatch, tmp_path):
    """A queued path without a widget id must not raise.

    The service died on the assertion, the widgets kept showing
    "Loading content..." forever, see
    https://github.com/drinfernoo/plugin.program.autowidget/issues/129
    """
    _profile(monkeypatch, tmp_path)

    monkeypatch.setattr(
        cache, "cache_files", lambda path, widget_id: ([], True)
    )

    assert cache.cache_and_update(PATH, None, None) == []


def test_cache_and_update_survives_a_missing_history(monkeypatch, tmp_path):
    _profile(monkeypatch, tmp_path)

    monkeypatch.setattr(cache, "cache_files", lambda path, widget_id: ([], True))

    widgets = cache.cache_and_update(PATH, "widget-id", None)
    assert widgets == ["widget-id"]


def test_cache_and_update_returns_the_widgets_of_the_path(monkeypatch, tmp_path):
    _profile(monkeypatch, tmp_path)

    monkeypatch.setattr(cache, "cache_files", lambda path, widget_id: ([], True))

    history = {"widgets": ["one", "two"], "path": PATH}
    widgets = cache.cache_and_update(PATH, "one", history)
    assert sorted(widgets) == ["one", "two"]


def test_the_widget_is_registered_for_the_path(monkeypatch, tmp_path):
    _profile(monkeypatch, tmp_path)

    payload = {"result": {"files": [{"label": "one", "file": "one.mkv"}]}}
    cache.cache_expiry(PATH, "widget-id", add=payload)

    history_path = os.path.join(
        str(tmp_path), "{}.history".format(cache.path2hash(PATH))
    )
    assert utils.read_json(history_path)["widgets"] == ["widget-id"]
