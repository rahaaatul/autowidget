from resources.lib import edit


PATHS = [
    {"id": "shows-1", "label": "Trending shows"},
    {"id": "movies-1", "label": "Trending movies"},
]


def _patch_paths(monkeypatch):
    monkeypatch.setattr(
        edit.manage, "get_path_by_id", lambda path_id, group_id=None: next(
            (p for p in PATHS if p["id"] == path_id), {}
        )
    )
    monkeypatch.setattr(
        edit.manage, "find_defined_paths", lambda group_id=None: PATHS
    )


def test_widget_options_resolve_the_path_ids(monkeypatch):
    """A widget stores the ids of its paths, not the path definitions.

    Reading them as dictionaries raised a TypeError in the edit dialog.
    """
    _patch_paths(monkeypatch)

    widget_def = {
        "action": "merged",
        "group": "group-1",
        "path": ["shows-1", "movies-1"],
    }

    options = edit._get_widget_options(widget_def)

    assert any("Trending shows, Trending movies" in option for option in options)


def test_widget_options_resolve_a_single_path(monkeypatch):
    _patch_paths(monkeypatch)

    widget_def = {"action": "static", "group": "group-1", "path": "movies-1"}

    options = edit._get_widget_options(widget_def)

    assert any("Trending movies" in option for option in options)


def test_widget_options_support_legacy_path_definitions(monkeypatch):
    """Widgets created before 3.3.0 stored the whole path definition."""
    _patch_paths(monkeypatch)

    widget_def = {
        "action": "merged",
        "group": "group-1",
        "path": [PATHS[0], PATHS[1]],
    }

    options = edit._get_widget_options(widget_def)

    assert any("Trending shows, Trending movies" in option for option in options)


def test_widget_options_fall_back_to_the_path_id(monkeypatch):
    _patch_paths(monkeypatch)

    widget_def = {
        "action": "merged",
        "group": "group-1",
        "path": ["gone-1"],
    }

    options = edit._get_widget_options(widget_def)

    assert any("gone-1" in option for option in options)


def test_widget_value_stores_the_path_ids(monkeypatch, kodi):
    """The stored paths have to keep the format the add-on uses."""
    _patch_paths(monkeypatch)
    kodi.dialog_answers["multiselect"] = [1]

    widget_def = {
        "action": "merged",
        "group": "group-1",
        "path": ["shows-1", "movies-1"],
    }

    assert edit._get_widget_value(widget_def, "path") == ["movies-1"]


def test_widget_value_stores_a_single_path_id(monkeypatch, kodi):
    _patch_paths(monkeypatch)
    kodi.dialog_answers["select"] = 1

    widget_def = {"action": "static", "group": "group-1", "path": "shows-1"}

    assert edit._get_widget_value(widget_def, "path") == "movies-1"
