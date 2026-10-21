import os

from resources.lib.common import utils

KODI_21_FIELDS = [
    "title",
    "artist",
    "album",
    "duration",
    "file",
    "art",
    "cast",
    "songvideourl",
    "userrating",
]


def _introspect_response():
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "types": {"List.Fields.Files": {"items": {"enums": KODI_21_FIELDS}}}
        },
    }


def test_to_text_handles_none_bytes_and_numbers():
    assert utils.to_text(None) is None
    assert utils.to_text(b"abc") == "abc"
    assert utils.to_text("abc") == "abc"
    assert utils.to_text(42) == "42"


def test_to_text_decodes_utf8():
    assert utils.to_text("é".encode()) == "é"


def test_convert_keeps_plain_values():
    assert utils.convert("text") == "text"
    assert utils.convert(7) == 7
    assert utils.convert(["a", "b"]) == ["a", "b"]


def test_get_valid_filename_strips_invalid_characters():
    assert "/" not in utils.get_valid_filename("a/b")
    assert ":" not in utils.get_valid_filename("a:b")


def test_free_memory_is_parsed_from_the_infolabel(monkeypatch):
    monkeypatch.setattr(utils.xbmc, "getInfoLabel", lambda label: "1234MB")
    assert utils.get_free_memory_mb() == 1234.0


def test_free_memory_is_none_when_unavailable(monkeypatch):
    monkeypatch.setattr(utils.xbmc, "getInfoLabel", lambda label: "")
    assert utils.get_free_memory_mb() is None


def test_free_memory_is_none_for_garbage(monkeypatch):
    monkeypatch.setattr(utils.xbmc, "getInfoLabel", lambda label: "unknown")
    assert utils.get_free_memory_mb() is None


def test_info_keys_are_introspected_from_kodi(monkeypatch):
    utils._info_keys = None
    monkeypatch.setattr(utils, "call_jsonrpc", lambda params: _introspect_response())
    assert utils.get_info_keys() == KODI_21_FIELDS


def test_info_keys_are_cached(monkeypatch):
    utils._info_keys = None
    calls = []

    def call_jsonrpc(params):
        calls.append(params)
        return _introspect_response()

    monkeypatch.setattr(utils, "call_jsonrpc", call_jsonrpc)
    utils.get_info_keys()
    utils.get_info_keys()
    assert len(calls) == 1


def test_info_keys_fall_back_when_kodi_cannot_be_introspected(monkeypatch):
    utils._info_keys = None

    def boom(params):
        raise RuntimeError("no json-rpc")

    monkeypatch.setattr(utils, "call_jsonrpc", boom)
    keys = utils.get_info_keys()
    assert keys == utils._default_info_keys
    assert "songvideourl" in keys


def test_default_info_keys_match_the_kodi_21_field_set():
    # The fallback has to be a valid property list for the targeted Kodi
    # release, otherwise the JSON-RPC call would fail entirely.
    assert "songvideourl" in utils._default_info_keys
    assert "userrating" in utils._default_info_keys
    assert len(utils._default_info_keys) == len(set(utils._default_info_keys))


def test_log_uses_the_info_level(monkeypatch):
    logged = []
    monkeypatch.setattr(utils.xbmc, "log", lambda msg, level: logged.append(level))
    utils.log("hello", "info")
    assert logged[-1] == utils.xbmc.LOGINFO
    utils.log("hello", "warning")
    assert logged[-1] == utils.xbmc.LOGWARNING
    utils.log("hello", "error")
    assert logged[-1] == utils.xbmc.LOGERROR


def test_clean_artwork_url_keeps_local_paths_absolute():
    """Local artwork has to stay absolute.

    Kodi treats an absolute path as a full path, a "special://" url can be
    mistaken for a skin relative one, which broke the artwork of the
    add-on's own icons in skins like Arctic Fuse 3.
    """
    local = os.path.join(
        utils._addon_root, "resources", "media", "fanart", "folder.png"
    )
    cleaned = utils.clean_artwork_url(local)
    assert cleaned == local
    assert "special://" not in cleaned


def test_clean_artwork_url_keeps_remote_urls():
    remote = "https://image.tmdb.org/t/p/w500/abc.jpg"
    assert utils.clean_artwork_url(remote) == remote


def test_clean_artwork_url_turns_special_home_urls_into_absolute_paths():
    """Caches written by older versions are repaired when they are read."""
    cleaned = utils.clean_artwork_url("special://home/Thumbnails/1/abc.jpg")
    assert cleaned == os.path.join(utils._home, "Thumbnails", "1", "abc.jpg")
    assert "special://" not in cleaned


def test_clean_artwork_url_strips_the_image_wrapper():
    assert utils.clean_artwork_url("image:///tmp/poster.jpg") == "/tmp/poster.jpg"
    assert (
        utils.clean_artwork_url("image:///tmp/poster.jpg@320x320")
        == "image:///tmp/poster.jpg@320x320"
    )


def test_refresh_plugin_container_reloads_the_autowidget_container(monkeypatch):
    builtins = []
    monkeypatch.setattr(
        utils.xbmc,
        "executebuiltin",
        lambda command, wait=False: builtins.append(command),
    )
    monkeypatch.setattr(utils, "get_active_window", lambda: "media")
    monkeypatch.setattr(
        utils, "get_infolabel", lambda label: "plugin.program.autowidget"
    )

    utils.refresh_plugin_container()

    assert builtins == ["Container.Refresh()"]


def test_refresh_plugin_container_does_nothing_for_other_containers(monkeypatch):
    builtins = []
    monkeypatch.setattr(
        utils.xbmc,
        "executebuiltin",
        lambda command, wait=False: builtins.append(command),
    )
    monkeypatch.setattr(utils, "get_active_window", lambda: "media")
    monkeypatch.setattr(utils, "get_infolabel", lambda label: "plugin.video.other")

    utils.refresh_plugin_container()

    assert builtins == []


def test_refresh_plugin_container_does_nothing_outside_a_media_window(monkeypatch):
    builtins = []
    monkeypatch.setattr(
        utils.xbmc,
        "executebuiltin",
        lambda command, wait=False: builtins.append(command),
    )
    monkeypatch.setattr(utils, "get_active_window", lambda: "home")
    monkeypatch.setattr(
        utils, "get_infolabel", lambda label: "plugin.program.autowidget"
    )

    utils.refresh_plugin_container()

    assert builtins == []


def test_update_container_reloads_the_container_during_a_scan(monkeypatch, kodi):
    """A scan must not stop the container from being reloaded."""
    builtins = []
    monkeypatch.setattr(
        utils.xbmc,
        "executebuiltin",
        lambda command, wait=False: builtins.append(command),
    )
    monkeypatch.setattr(utils, "get_active_window", lambda: "media")
    monkeypatch.setattr(
        utils, "get_infolabel", lambda label: "plugin.program.autowidget"
    )
    monkeypatch.setattr(utils, "get_condition", lambda condition: True)

    utils.update_container(True)

    assert builtins == ["Container.Refresh()"]


def test_update_container_does_not_update_the_library_during_a_scan(monkeypatch, kodi):
    """A library update while a scan is running would start another one."""
    builtins = []
    monkeypatch.setattr(
        utils.xbmc,
        "executebuiltin",
        lambda command, wait=False: builtins.append(command),
    )
    monkeypatch.setattr(utils, "get_active_window", lambda: "home")
    monkeypatch.setattr(utils, "get_condition", lambda condition: True)

    utils.update_container(True)

    assert builtins == []
