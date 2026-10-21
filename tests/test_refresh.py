from resources.lib import refresh


def test_refresh_keeps_working_when_a_path_disappeared(monkeypatch):
    """A widget can point at a path that was deleted in the meantime.

    Refreshing such a widget used to raise an AttributeError, see
    https://github.com/drinfernoo/plugin.program.autowidget/pull/140
    """
    saved = {}

    def save_path_details(widget_def, path_def=None, update=None):
        saved.update(widget_def)

    monkeypatch.setattr(refresh.manage, "get_widget_by_id", lambda widget_id: {})
    monkeypatch.setattr(refresh.manage, "find_defined_paths", lambda group_id=None: [])
    monkeypatch.setattr(refresh.manage, "save_path_details", save_path_details)
    monkeypatch.setattr(
        refresh.manage, "get_path_by_id", lambda path_id, group_id=None: {}
    )
    monkeypatch.setattr(refresh.utils, "update_container", lambda reload=False: None)

    widget_def = {
        "id": "1",
        "group": "group-1",
        "action": "cycling",
        "path": "missing-path",
        "cycle_paths": ["missing-path"],
        "refresh": 1,
        "updated": 0,
    }

    paths = refresh.refresh("1", widget_def=widget_def, force=True)

    assert paths == []
    # The widget keeps its path, it is just not updated any more
    assert widget_def["path"] == "missing-path"
    assert saved == {}
