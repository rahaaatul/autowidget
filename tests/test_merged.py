"""Tests for the merged widget flow.

A merged widget merges the paths of its group.  The paths can be changed
later with the "Paths" action of the widget.  The add-on never asks for the
paths on its own, a dialog on top of a skin widget would show up on every
start of Kodi.
"""

import pytest

from resources.lib import edit, manage, menu


@pytest.fixture(autouse=True)
def plugin_arguments(monkeypatch, kodi):
    """The add-on is called with a plugin url and a handle."""
    monkeypatch.setattr("sys.argv", ["plugin://plugin.program.autowidget/", "42"])
    kodi.directory_items.clear()
    kodi.dialog_calls.clear()


PATHS = [
    {"id": "shows-1", "label": "Trending shows", "file": {}},
    {"id": "movies-1", "label": "Trending movies", "file": {}},
]

GROUP = {
    "id": "group-1",
    "label": "Trending",
    "type": "widget",
    "paths": PATHS,
    "content": "videos",
}

def _merged_widget(**overrides):
    """A fresh copy of the widget definition."""
    widget = dict(
        id="widget-1",
        action="merged",
        group="group-1",
        path=["shows-1", "movies-1"],
    )
    widget.update(overrides)
    return widget


MERGED_WIDGET = {
    "id": "widget-1",
    "action": "merged",
    "group": "group-1",
    "path": ["shows-1", "movies-1"],
}

STATIC_WIDGET = {
    "id": "widget-2",
    "action": "static",
    "group": "group-1",
    "path": "shows-1",
}


def _patch_group(monkeypatch, widget_def=None):
    monkeypatch.setattr(
        manage, "get_group_by_id", lambda group_id, *args, **kwargs: GROUP
    )
    monkeypatch.setattr(
        manage,
        "get_widget_by_id",
        lambda widget_id, group_id=None: widget_def if widget_def else {},
    )
    monkeypatch.setattr(
        manage,
        "get_path_by_id",
        lambda path_id, group_id=None: next(
            (p for p in PATHS if p["id"] == path_id), {}
        ),
    )
    monkeypatch.setattr(menu.utils, "update_container", lambda reload=False: None)


def test_merged_path_merges_every_path(monkeypatch):
    """A merged widget uses all the paths of its group, without asking."""
    _patch_group(monkeypatch)
    saved = {}

    def initialize(group_def, action, widget_id, save=True, keep=None):
        saved["action"] = action
        saved["keep"] = keep
        return {
            "id": widget_id,
            "action": action,
            "path": [PATHS[idx]["id"] for idx in keep],
        }

    monkeypatch.setattr(manage, "initialize", initialize)

    menu.merged_path("group-1", "widget-1")

    assert saved["action"] == "merged"
    assert saved["keep"] == [0, 1]


def test_merged_path_does_not_open_a_dialog(monkeypatch, kodi):
    _patch_group(monkeypatch)
    monkeypatch.setattr(
        manage,
        "initialize",
        lambda group_def, action, widget_id, save=True, keep=None: {
            "id": widget_id,
            "action": action,
            "path": [PATHS[idx]["id"] for idx in keep],
        },
    )

    menu.merged_path("group-1", "widget-1")

    assert [call[0] for call in kodi.dialog_calls] == []


def test_merged_widget_is_labelled_and_has_the_paths_action(monkeypatch, kodi):
    """The "Paths" action belongs to the merged entry of the group."""
    _patch_group(monkeypatch, widget_def=MERGED_WIDGET)
    monkeypatch.setattr(manage, "clean", lambda all=False: [MERGED_WIDGET])
    monkeypatch.setattr(
        manage, "find_defined_widgets", lambda group_id=None: [_merged_widget()]
    )

    menu.active_widgets_menu()

    assert len(kodi.directory_items) == 1
    _url, item, _is_folder = kodi.directory_items[0]

    assert item.label == "Trending (Merged)"

    # The paths are changed from the merged entry of the group, not from
    # the list of the active widgets.
    assert "Paths" not in [entry[0] for entry in item.context_menu]


def test_the_merged_entry_of_the_group_has_the_paths_action(monkeypatch, kodi):
    _patch_group(monkeypatch)
    monkeypatch.setattr(
        manage, "get_group_by_id", lambda group_id, *args, **kwargs: GROUP
    )

    menu.group_menu("group-1")

    merged = [
        item
        for _url, item, _is_folder in kodi.directory_items
        if item.label == "Trending (Merged)"
    ]
    assert merged, [item.label for _url, item, _f in kodi.directory_items]

    labels = [entry[0] for entry in merged[0].context_menu]
    assert "Paths" in labels

    paths_action = dict(merged[0].context_menu)["Paths"]
    assert "action=edit_merged" in paths_action
    assert "group=group-1" in paths_action


def test_other_entries_of_the_group_have_no_paths_action(monkeypatch, kodi):
    _patch_group(monkeypatch)
    monkeypatch.setattr(
        manage, "get_group_by_id", lambda group_id, *args, **kwargs: GROUP
    )

    menu.group_menu("group-1")

    for _url, item, _is_folder in kodi.directory_items:
        if item.label != "Trending (Merged)":
            assert "Paths" not in [entry[0] for entry in item.context_menu]


def test_edit_merged_widget_saves_the_selected_paths(monkeypatch, kodi):
    _patch_group(monkeypatch, widget_def=dict(MERGED_WIDGET))
    monkeypatch.setattr(
        manage, "find_defined_widgets", lambda group_id=None: [_merged_widget()]
    )
    saved = {}
    monkeypatch.setattr(
        manage, "save_path_details", lambda params: saved.update(params)
    )
    kodi.dialog_answers["multiselect"] = [0]

    edit.edit_merged_widget("group-1")

    assert saved["path"] == ["shows-1"]


def test_edit_merged_widget_preselects_the_current_paths(monkeypatch, kodi):
    _patch_group(monkeypatch)
    monkeypatch.setattr(
        manage,
        "find_defined_widgets",
        lambda group_id=None: [_merged_widget(path=["movies-1"])],
    )
    monkeypatch.setattr(manage, "save_path_details", lambda params: None)

    edit.edit_merged_widget("group-1")

    calls = [call for call in kodi.dialog_calls if call[0] == "multiselect"]
    assert calls
    _name, args, kwargs = calls[-1]
    assert kwargs["preselect"] == [1]
    assert args[1] == ["Trending shows", "Trending movies"]


def test_edit_merged_widget_keeps_the_paths_when_nothing_is_selected(
    monkeypatch, kodi
):
    _patch_group(monkeypatch, widget_def=dict(MERGED_WIDGET))
    monkeypatch.setattr(
        manage, "find_defined_widgets", lambda group_id=None: [_merged_widget()]
    )
    saved = {}
    monkeypatch.setattr(
        manage, "save_path_details", lambda params: saved.update(params)
    )
    kodi.dialog_answers["multiselect"] = []

    edit.edit_merged_widget("group-1")

    assert saved == {}


def test_edit_merged_widget_picks_the_most_recent_widget(monkeypatch, kodi):
    """A group can have more than one merged widget."""
    older = _merged_widget(id="widget-old", path=["shows-1"], updated=100)
    newer = _merged_widget(id="widget-new", path=["movies-1"], updated=200)
    _patch_group(monkeypatch)
    monkeypatch.setattr(
        manage, "find_defined_widgets", lambda group_id=None: [older, newer]
    )
    saved = {}
    monkeypatch.setattr(
        manage, "save_path_details", lambda params: saved.update(params)
    )
    kodi.dialog_answers["multiselect"] = [1]

    edit.edit_merged_widget("group-1")

    assert saved["id"] == "widget-new"
