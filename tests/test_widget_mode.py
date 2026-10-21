import pytest
from resources.lib import menu
from resources.lib.common import utils


@pytest.fixture(autouse=True)
def reset_widget_mode():
    """Every test starts without an explicit widget mode."""
    utils.set_widget_mode(None)
    yield
    utils.set_widget_mode(None)


def test_widget_mode_is_off_by_default(kodi):
    assert utils.is_widget_mode() is False


def test_widget_mode_is_requested_in_the_plugin_url():
    utils.set_widget_mode_from_params({"widget": "true"})
    assert utils.is_widget_mode() is True


@pytest.mark.parametrize("value", ["True", "1", "yes", "on", "TRUE"])
def test_widget_mode_accepts_the_usual_truthy_values(value):
    utils.set_widget_mode_from_params({"widget": value})
    assert utils.is_widget_mode() is True


@pytest.mark.parametrize("value", ["false", "0", "no", "off", "maybe"])
def test_widget_mode_accepts_falsy_values(value):
    utils.set_widget_mode_from_params({"widget": value})
    assert utils.is_widget_mode() is False


def test_widget_mode_is_not_set_without_the_parameter():
    utils.set_widget_mode_from_params({"mode": "path"})
    assert utils._widget_mode is None


def test_widget_mode_is_detected_in_skin_shortcuts(kodi):
    kodi.set_cond_visibility("Window.IsVisible(script-skinshortcuts.xml)")
    assert utils.is_skin_shortcut() is True
    assert utils.is_widget_mode() is True


def test_widget_mode_is_detected_from_the_home_window_property(kodi):
    kodi.set_info_label("Window(Home).Property(AutoWidget.WidgetMode)", "true")
    assert utils.is_skin_shortcut() is True
    assert utils.is_widget_mode() is True


def test_an_explicit_widget_mode_wins_over_the_detection(kodi):
    kodi.set_cond_visibility("Window.IsVisible(script-skinshortcuts.xml)")
    utils.set_widget_mode(False)
    assert utils.is_widget_mode() is False


def _prepare_listing(monkeypatch):
    monkeypatch.setattr("sys.argv", ["plugin://plugin.program.autowidget/", "42"])
    monkeypatch.setattr(
        menu.manage,
        "get_widget_by_id",
        lambda *args, **kwargs: {"action": "static", "path": "path-id", "stack": []},
    )
    monkeypatch.setattr(
        menu.refresh,
        "get_files_list",
        lambda *args, **kwargs: (
            [
                {
                    "label": "A movie",
                    "file": "/movies/a.mkv",
                    "type": "movie",
                    "filetype": "file",
                }
            ],
            "hash",
        ),
    )
    monkeypatch.setattr(
        menu.settings, "get_setting_bool", lambda *args, **kwargs: False
    )
    monkeypatch.setattr(menu.settings, "get_setting_int", lambda *args, **kwargs: 0)
    monkeypatch.setattr(
        menu.settings, "get_setting_string", lambda *args, **kwargs: "white"
    )

    widget_path = {"file": {"file": "/movies/"}, "content": "movies"}
    return menu.show_path("group-id", "A label", "widget-id", widget_path)


def test_a_normal_listing_carries_the_management_actions(monkeypatch, kodi):
    utils.set_widget_mode(False)
    _prepare_listing(monkeypatch)

    item = kodi.directory_items[-1][1]
    assert item.getProperty("autoID") == "widget-id"
    assert item.getProperty("autoCache") == "hash"


def test_a_widget_listing_has_no_management_actions(monkeypatch, kodi):
    utils.set_widget_mode(True)
    _prepare_listing(monkeypatch)

    item = kodi.directory_items[-1][1]
    assert item.getProperty("autoID") == ""
    assert item.getProperty("autoAction") == ""
    assert item.getProperty("autoCache") == ""
    assert item.getProperty("autoLabel") == "A label"


def _prepare_group(monkeypatch, calls):
    monkeypatch.setattr("sys.argv", ["plugin://plugin.program.autowidget/", "42"])
    monkeypatch.setattr(
        menu.manage,
        "get_group_by_id",
        lambda *args, **kwargs: {
            "id": "group-id",
            "label": "Group",
            "type": "widget",
            "paths": [
                {"id": "path-id", "label": "A path", "file": {"file": "/movies/"}}
            ],
        },
    )
    monkeypatch.setattr(menu.manage, "get_widget_by_id", lambda *args, **kwargs: {})
    monkeypatch.setattr(
        menu.manage,
        "get_path_by_id",
        lambda *args, **kwargs: {"label": "A path", "file": {"file": "/movies/"}},
    )

    def fake_choose_paths(*args, **kwargs):
        calls.append("choose_paths")
        return 0

    def fake_initialize(group_def, action, widget_id, keep=None, **kwargs):
        calls.append(("initialize", action, keep))
        return {"id": widget_id, "action": action, "path": "path-id", "stack": []}

    monkeypatch.setattr(menu.manage, "choose_paths", fake_choose_paths)
    monkeypatch.setattr(menu.manage, "initialize", fake_initialize)
    monkeypatch.setattr(
        menu.refresh, "get_files_list", lambda *args, **kwargs: ([], "hash")
    )
    monkeypatch.setattr(
        menu.settings, "get_setting_bool", lambda *args, **kwargs: False
    )
    monkeypatch.setattr(menu.settings, "get_setting_int", lambda *args, **kwargs: 0)
    monkeypatch.setattr(
        menu.settings, "get_setting_string", lambda *args, **kwargs: "white"
    )


def test_a_widget_never_asks_which_path_to_use(monkeypatch, kodi):
    utils.set_widget_mode(True)
    calls = []
    _prepare_group(monkeypatch, calls)

    menu.path_menu("group-id", "static", "widget-id")

    assert "choose_paths" not in calls
    assert ("initialize", "static", 0) in calls


def test_a_normal_listing_asks_which_path_to_use(monkeypatch, kodi):
    utils.set_widget_mode(False)
    calls = []
    _prepare_group(monkeypatch, calls)

    menu.path_menu("group-id", "static", "widget-id")

    assert "choose_paths" in calls
