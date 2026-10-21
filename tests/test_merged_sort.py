"""Tests for the sort of the items of a merged widget.

The items of the merged paths are shown path by path, the sort puts them
in one list.
"""

import pytest
from resources.lib import menu


@pytest.fixture(autouse=True)
def plugin_arguments(monkeypatch, kodi):
    """The add-on is called with a plugin url and a handle."""
    monkeypatch.setattr("sys.argv", ["plugin://plugin.program.autowidget/", "42"])
    kodi.directory_items.clear()
    kodi.dialog_calls.clear()


def _item(label, **info):
    """A list item as show_path collects it."""
    file = {"label": label, "file": f"plugin://path/{label}", "filetype": "file"}
    file.update(info)
    return {"title": label, "path": file["file"], "info": file, "isFolder": False}


def _merged_items():
    return [
        _item("Shows", type="tvshow", premiered="2026-10-13", year=2026, rating=8.8),
        _item("Movies", type="movie", premiered="2026-07-29", year=2026, rating=7.2),
        _item("Old", type="movie", premiered="2019-01-05", year=2019, rating=9.4),
    ]


def _sorted_items(monkeypatch, sort):
    monkeypatch.setattr(menu.settings, "get_setting_int", lambda setting: sort)
    return menu._sort_merged_items(_merged_items())


def test_the_items_keep_the_order_of_the_paths_without_a_sort(monkeypatch):
    items = _sorted_items(monkeypatch, 0)

    assert [item["title"] for item in items] == ["Shows", "Movies", "Old"]


def test_the_items_are_sorted_by_date_newest_first(monkeypatch):
    items = _sorted_items(monkeypatch, 1)

    assert [item["title"] for item in items] == ["Shows", "Movies", "Old"]


def test_the_items_are_sorted_by_date_oldest_first(monkeypatch):
    items = _sorted_items(monkeypatch, 2)

    assert [item["title"] for item in items] == ["Old", "Movies", "Shows"]


def test_the_items_are_sorted_by_rating(monkeypatch):
    items = _sorted_items(monkeypatch, 3)

    assert [item["title"] for item in items] == ["Old", "Shows", "Movies"]


def test_the_items_are_sorted_by_title(monkeypatch):
    items = _sorted_items(monkeypatch, 4)

    assert [item["title"] for item in items] == ["Movies", "Old", "Shows"]


def test_the_items_are_sorted_by_year(monkeypatch):
    items = _sorted_items(monkeypatch, 5)

    assert [item["title"] for item in items] == ["Shows", "Movies", "Old"]


def test_items_without_a_date_are_shown_last(monkeypatch):
    monkeypatch.setattr(menu.settings, "get_setting_int", lambda setting: 1)
    items = [
        _item("No date", type="movie"),
        _item("Dated", type="movie", premiered="2026-07-29", year=2026),
    ]

    sorted_items = menu._sort_merged_items(items)

    assert [item["title"] for item in sorted_items] == ["Dated", "No date"]


def test_the_year_is_used_when_an_item_has_no_date(monkeypatch):
    monkeypatch.setattr(menu.settings, "get_setting_int", lambda setting: 1)
    items = [
        _item("Old show", type="tvshow", year=2019),
        _item("New show", type="tvshow", year=2026),
    ]

    sorted_items = menu._sort_merged_items(items)

    assert [item["title"] for item in sorted_items] == ["New show", "Old show"]


def test_merged_path_shows_the_items_of_all_paths_in_one_list(monkeypatch, kodi):
    """The items of the merged paths are one list, not one list per path."""
    paths = {
        "shows-1": {
            "id": "shows-1",
            "label": "Shows",
            "file": {"file": "plugin://shows"},
        },
        "movies-1": {
            "id": "movies-1",
            "label": "Movies",
            "file": {"file": "plugin://movies"},
        },
    }
    group = {
        "id": "group-1",
        "label": "Trending",
        "type": "widget",
        "paths": list(paths.values()),
    }
    widget = {
        "id": "widget-1",
        "action": "merged",
        "group": "group-1",
        "path": ["shows-1", "movies-1"],
    }

    monkeypatch.setattr(
        menu.manage, "get_group_by_id", lambda group_id, *args, **kwargs: group
    )
    monkeypatch.setattr(
        menu.manage, "get_widget_by_id", lambda widget_id, group_id=None: widget
    )
    monkeypatch.setattr(
        menu.manage,
        "get_path_by_id",
        lambda path_id, group_id=None: paths.get(path_id, {}),
    )
    files = {
        "plugin://shows": [
            {
                "label": "The Show",
                "file": "plugin://shows/1",
                "filetype": "file",
                "type": "tvshow",
                "premiered": "2020-01-01",
                "year": 2020,
            }
        ],
        "plugin://movies": [
            {
                "label": "The Movie",
                "file": "plugin://movies/1",
                "filetype": "file",
                "type": "movie",
                "premiered": "2026-07-29",
                "year": 2026,
            }
        ],
    }
    monkeypatch.setattr(
        menu.refresh,
        "get_files_list",
        lambda path, label, widget_id: (files.get(path, []), "hash"),
    )
    monkeypatch.setattr(menu.utils, "is_widget_mode", lambda: False)

    kodi.addon_settings.setdefault("plugin.program.autowidget", {})[
        "widgets.merged_sort"
    ] = 1

    menu.merged_path("group-1", "widget-1")

    labels = [item.label for _url, item, _is_folder in kodi.directory_items]
    # The path of the shows comes first, the date sort puts the movie first
    assert labels == ["The Movie", "The Show"]


def test_the_sort_of_the_widget_wins_over_the_setting(monkeypatch, kodi):
    """The widget has its own sort, the setting is the default."""
    monkeypatch.setattr(menu.settings, "get_setting_int", lambda setting: 1)
    items = [
        _item("Old", type="movie", premiered="2019-01-05", year=2019),
        _item("New", type="movie", premiered="2026-07-29", year=2026),
    ]

    sorted_items = menu._sort_merged_items(items, {"sort": 2})

    assert [item["title"] for item in sorted_items] == ["Old", "New"]


def test_the_setting_is_used_when_the_widget_has_no_sort(monkeypatch, kodi):
    monkeypatch.setattr(menu.settings, "get_setting_int", lambda setting: 1)
    items = [
        _item("Old", type="movie", premiered="2019-01-05", year=2019),
        _item("New", type="movie", premiered="2026-07-29", year=2026),
    ]

    sorted_items = menu._sort_merged_items(items, {})

    assert [item["title"] for item in sorted_items] == ["New", "Old"]


def test_the_merged_entry_has_the_sort_action(monkeypatch, kodi):
    from resources.lib import manage

    group = {
        "id": "group-1",
        "label": "Trending",
        "type": "widget",
        "paths": [
            {"id": "shows-1", "label": "Shows", "file": {"file": "plugin://shows"}}
        ],
    }
    monkeypatch.setattr(
        manage, "get_group_by_id", lambda group_id, *args, **kwargs: group
    )
    monkeypatch.setattr(manage, "get_merged_widget", lambda group_id: {})

    menu.group_menu("group-1")

    merged = [item for _url, item, _f in kodi.directory_items if "Merged" in item.label]
    labels = [entry[0] for entry in merged[0].context_menu]
    assert "Paths" in labels
    assert "Sort" in labels

    sort_action = dict(merged[0].context_menu)["Sort"]
    assert "action=edit_merged_sort" in sort_action


def test_the_sort_of_a_widget_is_saved(monkeypatch, kodi):
    from resources.lib import edit

    widget = {"id": "widget-1", "action": "merged", "group": "group-1"}
    monkeypatch.setattr(edit.manage, "get_merged_widget", lambda group_id: widget)
    saved = {}
    monkeypatch.setattr(
        edit.manage, "save_path_details", lambda params: saved.update(params)
    )
    kodi.dialog_answers["select"] = 1

    edit.edit_merged_sort("group-1")

    assert saved["sort"] == 1
