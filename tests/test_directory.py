import pytest
from resources.lib.common import directory


@pytest.mark.parametrize(
    "value,expected",
    [
        (90, 90),
        (90.5, 90),
        ("90", 90),
        ("01:23:45", 5025),
        ("23:45", 1425),
        ("00:00:30", 30),
        ("1:2:3", 3723),
    ],
)
def test_parse_duration(value, expected):
    assert directory.parse_duration(value) == expected


@pytest.mark.parametrize("value", ["", "   ", "abc", "1:2:3:4", None, [], {}])
def test_parse_duration_of_invalid_values(value):
    assert directory.parse_duration(value) is None


def test_add_menu_item_builds_the_plugin_url(monkeypatch):
    monkeypatch.setattr("sys.argv", ["plugin://plugin.program.autowidget/", "42"])
    url = directory.add_menu_item(title="Item", params={"mode": "group", "id": "1"})
    assert "mode=group" in url
    assert "id=1" in url


def test_add_menu_item_uses_a_direct_path(monkeypatch):
    monkeypatch.setattr("sys.argv", ["plugin://plugin.program.autowidget/", "42"])
    url = directory.add_menu_item(title="Item", path="plugin://other/")
    assert url == "plugin://other/"


def test_add_menu_item_converts_a_duration_string(monkeypatch, kodi):
    monkeypatch.setattr("sys.argv", ["plugin://plugin.program.autowidget/", "42"])
    directory.add_menu_item(
        title="Item", info={"type": "movie", "duration": "01:02:03"}
    )
    item = kodi.directory_items[-1][1]
    assert item.info["video"]["duration"] == 3723


def test_add_menu_item_wraps_the_artist_in_a_list(monkeypatch, kodi):
    monkeypatch.setattr("sys.argv", ["plugin://plugin.program.autowidget/", "42"])
    directory.add_menu_item(title="Item", info={"type": "song", "artist": "A"})
    item = kodi.directory_items[-1][1]
    assert item.info["music"]["artist"] == ["A"]


def test_add_menu_item_uses_set_cast(monkeypatch, kodi):
    monkeypatch.setattr("sys.argv", ["plugin://plugin.program.autowidget/", "42"])
    cast = [{"role": "Actor", "name": "Someone", "thumbnail": ""}]
    directory.add_menu_item(title="Item", info={"type": "movie", "cast": cast})
    item = kodi.directory_items[-1][1]
    assert item.cast == cast
    assert "cast" not in item.info.get("video", {})
