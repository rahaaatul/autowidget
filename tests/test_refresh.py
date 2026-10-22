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


def test_player_type_is_always_defined():
    """Playback can end without a start event reaching the service."""
    assert refresh.Player().type == "unknown"


def test_playback_ended_without_a_start_event_does_not_raise(monkeypatch):
    saved = []
    monkeypatch.setattr(
        refresh.cache,
        "save_playback_history",
        lambda playback_type, percentage, path: saved.append(playback_type),
    )
    monkeypatch.setattr(refresh.cache, "widgets_changed_by_watching", lambda kind: [])

    player = refresh.Player()
    player.onPlayBackEnded()

    assert saved == ["unknown"]
    assert player.type == "unknown"


def _service(playing_video=False, refresh_during_playback=False):
    """A service instance without starting any of its threads."""
    service = object.__new__(refresh.RefreshService)
    service.player = type(
        "Player", (), {"isPlayingVideo": lambda self: playing_video}
    )()
    service.refresh_during_playback = refresh_during_playback
    return service


def test_queue_waits_for_the_playback_to_end_by_default():
    """Without the opt-in the queue is not processed during playback."""
    service = _service(playing_video=True, refresh_during_playback=False)
    assert service._skip_for_playback() is True


def test_queue_is_processed_during_playback_when_enabled():
    service = _service(playing_video=True, refresh_during_playback=True)
    assert service._skip_for_playback() is False


def test_queue_is_processed_when_nothing_is_playing():
    service = _service(playing_video=False, refresh_during_playback=False)
    assert service._skip_for_playback() is False


def test_the_worker_marks_the_task_as_done(monkeypatch, kodi):
    """The counter of the queue has to go back to zero.

    Without task_done() it grows with every update and join() would hang.
    """
    service = object.__new__(refresh.RefreshService)
    service.queue = refresh.OrderedSetQueue()
    service.low_end = False
    service.player = type("Player", (), {"isPlayingVideo": lambda self: False})()
    service.refresh_during_playback = True

    aborts = []

    def abort_requested():
        aborts.append(True)
        # the worker stops after the first item
        return len(aborts) > 1

    service.abortRequested = abort_requested
    monkeypatch.setattr(refresh.cache, "cache_and_update", lambda *a, **k: set())

    service.queue.put(("hash", "plugin://path", "widget"))
    service._processQueue()

    assert service.queue.unfinished_tasks == 0
