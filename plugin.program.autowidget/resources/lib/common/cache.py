import hashlib
import json
import math
import os
import random
import threading
import time

import xbmc
import xbmcgui
import xbmcvfs

from resources.lib import manage
from resources.lib.common import settings, utils

_addon_data = settings.get_addon_info("profile")

_playback_history_path = os.path.join(_addon_data, "cache.history")

_startup_time = time.time()  # TODO: could get reloaded so not accurate?
DEFAULT_CACHE_TIME = 60 * 5

# The number of entries the histories keep.  The prediction of the next
# update only needs a few samples, the older ones describe a list that does
# not exist any more.
MAX_HISTORY_ENTRIES = 500

# How often the service is notified that a path has to be updated.
SEND_RETRIES = 30

# How long a content that never changed is trusted, the window the samples
# of the older versions covered.
MAX_CURRENT_STREAK = 30 * 24 * 60 * 60


def clear_cache(target=None):
    if not target:
        dialog = xbmcgui.Dialog()
        choice = dialog.yesno("AutoWidget", utils.get_string(30117))
        del dialog

        if choice:
            for file in [
                i
                for j in xbmcvfs.listdir(_addon_data)
                for i in j
                if i.endswith((".cache", ".history", ".queue", ".time"))
            ]:
                utils.remove_file(os.path.join(_addon_data, file))
    else:
        utils.remove_file(os.path.join(_addon_data, f"{target}.cache"))
        utils.update_container(True)


def hash_from_cache_path(path):
    base = os.path.basename(path)
    return os.path.splitext(base)[0]


def _read_history_file(history_path):
    """The history of a path, a history of an older version is migrated."""
    cache_data = utils.read_json(history_path, default={})
    if "changes" not in cache_data:
        # A history of an older version, it holds a sample on every update.
        # The content changed somewhere between two samples, the middle of
        # the two is the best guess.  The samples are not used any more.
        cache_data["changes"] = _changes_from_samples(cache_data.get("history", []))
        cache_data.pop("history", None)
        utils.write_json(history_path, cache_data)
    return cache_data


def read_history(path, create_if_missing=True):
    """The history of a path.

    Older versions wrote a sample on every update, the current one writes
    the changes only.  A history of an older version is migrated when it is
    read.
    """
    hash = path2hash(path)
    history_path = os.path.join(_addon_data, f"{hash}.history")
    if not xbmcvfs.exists(history_path):
        if create_if_missing:
            cache_data = {"widgets": [], "changes": []}
            utils.write_json(history_path, cache_data)
        else:
            cache_data = None
    else:
        cache_data = _read_history_file(history_path)
    return cache_data


def _changes_from_samples(history):
    """The changes of a path from the samples of an older version.

    A sample was written on every update, the content changed somewhere
    between two samples.  The middle of the two is the best guess.
    """
    changes = []
    for idx, (when, content) in enumerate(history):
        if idx == 0:
            changes.append((when, content))
            continue
        if content != history[idx - 1][1]:
            previous_when = history[idx - 1][0]
            changes.append(((previous_when + when) / 2, content))
    return changes


def push_cache_queue(path, widget_id=None):
    hash = path2hash(path)
    history = read_history(path, create_if_missing=True)  # Ensure its created
    changed = False
    if widget_id is not None and widget_id not in history["widgets"]:
        history["widgets"].append(widget_id)
        changed = True
    if history.get("path", "") != path:
        history["path"] = path
        changed = True
    # The widgets that are gone are not used any more, they would pile up in
    # the history file of the path.
    alive = [
        widget
        for widget in history["widgets"]
        if xbmcvfs.exists(os.path.join(_addon_data, f"{widget}.widget"))
    ]
    if len(alive) != len(history["widgets"]):
        history["widgets"] = alive
        changed = True
    if changed:
        history_path = os.path.join(_addon_data, f"{hash}.history")
        utils.write_json(history_path, history)

    command = {
        "jsonrpc": "2.0",
        "method": "JSONRPC.NotifyAll",
        "params": {
            "sender": "AutoWidget",
            "message": "queue",
            "data": (hash, path, widget_id),
        },
        "id": 1,
    }

    def send():
        # The service may not be running yet, it is notified when it starts.
        # The thread gives up after a while so that it cannot pile up.
        for _ in range(SEND_RETRIES):
            if utils.call_jsonrpc(command):
                return
            xbmc.sleep(1000)

    # Don't wait in case service hasn't started
    threading.Thread(target=send, daemon=True).start()


def path2hash(path):
    if path is not None:
        data = path.encode("utf-8") if isinstance(path, str) else path
        return hashlib.sha1(data).hexdigest()
    else:
        return None


def widgets_for_path(path):
    hash = path2hash(path)
    history_path = os.path.join(_addon_data, f"{hash}.history")
    cache_data = utils.read_json(history_path) if os.path.exists(history_path) else None
    if cache_data is None:
        cache_data = {}
    widgets = cache_data.setdefault("widgets", [])
    return set(widgets)


def cache_and_update(path, widget_id, cache_data, notify=None):
    """a widget might have many paths. Ensure each path is either queued for an update
    or is expired and if so force it to be refreshed. When going through the queue this
    could mean we refresh paths that other widgets also use. These will then be skipped.
    """
    if not cache_data:
        cache_data = read_history(path)

    widgets = cache_data.setdefault("widgets", [])
    if widget_id and widget_id not in widgets:
        widgets.append(widget_id)

    if notify is not None:
        widget_def = manage.get_widget_by_id(widget_id)
        if widget_def is not None:
            notify(widget_def.get("label", ""), path)

    new_files, files_changed = cache_files(path, widget_id)

    # TODO: this is all widgets that ever requested this path. do we
    # need to update all of them?
    return widgets if files_changed else []


def cache_files(path, widget_id):
    info_keys = utils.get_info_keys()
    params = {
        "jsonrpc": "2.0",
        "method": "Files.GetDirectory",
        "params": {
            "properties": info_keys,
            "directory": path,
        },
        "id": 1,
    }
    files = utils.call_jsonrpc(params)
    _, _, changed = cache_expiry(path, widget_id, add=files)
    return (files, changed)


def cache_expiry(path, widget_id, add=None, background=True):
    # Predict how long to cache for with a min of 5min so updates don't go in a loop
    # TODO: find better way to prevents loops so that users trying to manually refresh can do so
    # TODO: manage the cache files to remove any too old or no longer used
    # TODO: update paths on autowidget refresh based on predicted update frequency. e.g. plugins with random paths should
    # update when autowidget updates.
    hash = path2hash(path)
    cache_path = os.path.join(_addon_data, f"{hash}.cache")

    # Read file every time as we might be called from multiple processes
    history_path = os.path.join(_addon_data, f"{hash}.history")
    cache_data = (
        _read_history_file(history_path) if xbmcvfs.exists(history_path) else None
    )
    if cache_data is None:
        cache_data = {}
        since_read = 0
    else:
        since_read = time.time() - last_read(hash)

    changes = cache_data.setdefault("changes", [])
    widgets = cache_data.setdefault("widgets", [])
    if widget_id and widget_id not in widgets:
        widgets.append(widget_id)

    expiry = time.time() - 20
    contents = None
    changed = True
    size = 0

    if add is not None:
        cache_json = json.dumps(add)
        if not add or not cache_json.strip():
            result = "Invalid Write"

        elif "error" in add or not add.get("result", {}).get("files"):
            # In this case we don't want to cache a bad result
            result = "Error"
            # TODO: do we schedule a new update? or put dummy content up even if we have
            # good cached content?
        else:
            utils.write_json(cache_path, add)
            contents = add
            size = len(cache_json)
            content_hash = path2hash(cache_json)
            changed = changes[-1][1] != content_hash if changes else True
            if changed:
                # Only the changes are kept, a sample on every update would
                # make the file grow forever.
                changes.append((time.time(), content_hash))
                if len(changes) > MAX_HISTORY_ENTRIES:
                    del changes[:-MAX_HISTORY_ENTRIES]
            if cache_data.get("path") != path:
                cache_data["path"] = path
            utils.write_json(history_path, cache_data)
            # expiry = changes[-1][0] + DEFAULT_CACHE_TIME
            pred_dur = cache_lifetime(changes)
            expiry = (
                time.time() + pred_dur * 0.75
            )  # less than prediction to ensure pred keeps up to date
            result = "Wrote"
    else:
        # write any updated widget_ids so we know what to update when we dequeue
        # Also important as wwe use last modified of .history as accessed time
        utils.write_json(history_path, cache_data)
        if not xbmcvfs.exists(cache_path):
            result = "Empty"
            if background:
                contents = utils.make_holding_path(utils.get_string(30143), "refresh")
                push_cache_queue(path, widget_id)
        else:
            contents = utils.read_json(cache_path, log_file=True)
            if contents is None:
                result = "Invalid Read"
                if background:
                    contents = utils.make_holding_path(
                        utils.get_string(30137).format(hash), "alert"
                    )
                    push_cache_queue(path, widget_id)
            else:
                size = len(json.dumps(contents))
                if changes:
                    expiry = last_written(hash) + cache_lifetime(changes)

                #                queue_len = len(list(iter_queue()))
                if expiry > time.time():
                    result = "Read"
                elif not background:
                    result = "Skip already updated"
                # elif queue_len > 3:
                #     # Try to give system more breathing space by returning empty cache but ensuring refresh
                #     # better way is to just do this the first X accessed after startup.
                #     # or how many accessed in the last 30s?
                #     push_cache_queue(hash)
                #     result = "Skip (queue={})".format(queue_len)
                #     contents = dict(result=dict(files=[]))
                else:
                    push_cache_queue(path, widget_id)
                    result = "Read and queue"
    # TODO: some metric that tells us how long to the first and last widgets becomes visible and then get updated
    # not how to measure the time delay when when the cache is read until it appears on screen?
    # Is the first cache read always the top visibible widget?
    utils.log(
        f"{result} cache {size}B (exp:{utils.ft(expiry - time.time())}, last:{utils.ft(since_read)}): {hash[:5]} {widgets}",
        "notice",
    )
    return expiry, contents, changed


def last_read(hash):
    # Technically this is last read or updated but we can change it to be last read Later
    # if we create another file
    path = os.path.join(_addon_data, f"{hash}.history")
    return xbmcvfs.Stat(path).st_mtime()


def last_written(hash):
    """When the content of a path was written the last time.

    The history holds the changes of the content, the time of the last write
    is the time of the cache file.
    """
    path = os.path.join(_addon_data, f"{hash}.cache")
    if not xbmcvfs.exists(path):
        return 0
    try:
        return xbmcvfs.Stat(path).st_mtime()
    except Exception:
        return 0


def _minimum_lifetime():
    """The cache may not expire before the service refreshes it anyway.

    A lifetime that is shorter than the refresh interval of the service
    would make the reader ask for a refresh that the service is about to do
    anyway.
    """
    try:
        duration = settings.get_setting_float("service.refresh_duration")
    except Exception:
        duration = 0
    return duration * 60 * 60 / 2


def cache_lifetime(changes):
    """How long the content of a path may be cached."""
    return max(predict_update_frequency(changes), _minimum_lifetime())


def predict_update_frequency(changes, now=None):
    """How long the content of a path stays the same.

    The history holds the changes of the content: (time, hash).  The time
    between two changes is how long the content stayed the same, the longer
    it stays the same the longer the content may be cached.
    """
    if not changes:
        return DEFAULT_CACHE_TIME

    if now is None:
        now = time.time()

    durations = []
    for (when, _content), (next_when, _next_content) in zip(changes, changes[1:]):
        duration = next_when - when
        if duration > 0:
            durations.append(duration)

    if not durations:
        # The content never changed, it is the same since the first change.
        # The window is bounded, a list that starts to change after a year
        # of silence should not be cached for a year.
        durations.append(min(now - changes[0][0], MAX_CURRENT_STREAK))

    med_dur = sorted(durations)[int(math.floor(len(durations) / 2)) - 1]
    avg_dur = sum(durations) / len(durations)

    utils.log(
        f"avg_dur {avg_dur:0.0f}s, med_dur {med_dur:0.0f}s, all {durations}",
        "debug",
    )

    if avg_dur / 2.0 < DEFAULT_CACHE_TIME:
        # should not got less than 5min otherwise our updates go in a loop
        return DEFAULT_CACHE_TIME
    else:
        return (
            avg_dur / 2.0
        )  # we want to ensure we check more often than the actual predicted expiry


#    return DEFAULT_CACHE_TIME


def widgets_changed_by_watching(media_type):
    # Predict which widgets the skin might have that could have changed based on recently finish
    # watching something

    all_hist = [
        os.path.join(_addon_data, x)
        for x in xbmcvfs.listdir(_addon_data)[1]
        if x.endswith(".history")
    ]

    # Get rid of ones not read this session. These are old
    all_hist = [
        hist_path
        for hist_path in all_hist
        if (xbmcvfs.Stat(hist_path).st_mtime() - _startup_time) >= 0
    ]

    # Simple version. Anything updated recently (since startup?)
    # priority = sorted(all_cache, key=os.path.getmtime)
    # Sort by chance of it updating
    plays = utils.read_json(_playback_history_path, default={}).setdefault("plays", [])
    plays_for_type = [
        (time, t) for time, t in plays if t == media_type or media_type is None
    ]
    priority = sorted(
        [
            (
                chance_playback_updates_widget(cache_data, plays_for_type),
                cache_data.get("path", ""),
                hist_path,
            )
            for hist_path, cache_data in [(p, _read_history_file(p)) for p in all_hist]
        ],
        reverse=True,
    )

    count_prob_changed = 0
    randoms = 0
    i = 0
    for chance, path, _history_path in priority:
        hash = path2hash(path)
        if "page=" in path:
            # HACK: must be a better way
            continue
        elif chance >= 0.3 or i < 7:
            utils.log(
                f"Queue {chance * 100:.2f}% {hash[:5]} {path}",
                "notice",
            )
            count_prob_changed += 1
            yield hash, path
        elif random.random() <= (1 / len(priority)):
            # If widgets never get updated after playback we never get to know if they change after playback. So always pick some randomly
            utils.log(f"Queue random {chance * 100:.2f}% {hash[:5]} {path}", "notice")
            randoms += 1
            yield hash, path
        else:
            utils.log(
                f"Prob not changes due to playback {chance * 100:.2f}% {hash[:5]} {path}",
                "notice",
            )
        i += 1
    utils.log(
        f"=== End Widget update: {count_prob_changed} prob changed after playback {randoms} randoms",
        "notice",
    )


def chance_playback_updates_widget(cache_data, plays, cutoff_time=60 * 60):
    """How likely it is that a playback changed the content of a path.

    The history holds the changes of the content, so for every playback the
    first change after it tells whether the playback changed the content.
    """
    changes = cache_data.setdefault("changes", [])
    hist_len = len(changes)
    path = cache_data.get("path", "")
    # Complex version
    # - for each widget
    #    - come up with chance it will update after a playback
    #    - each pair of updates, is there a playback inbetween and updated with X min after playback
    #    - num playback with change / num playback with no change
    # C C P C C
    changed, non_changes, unrelated_changes, too_late_changes = 0, 0, 0, 0

    change_times = [when for when, _content in changes]
    change_idx = 0

    for play_time, _media_type in sorted(plays):
        # The changes before this playback were not caused by it.
        while change_idx < len(change_times) and change_times[change_idx] < play_time:
            unrelated_changes += 1
            change_idx += 1

        if change_idx >= len(change_times):
            # The playback did not change the content.
            non_changes += 1
        elif change_times[change_idx] - play_time <= cutoff_time:
            # The content changed shortly after the playback.
            changed += 1
            change_idx += 1
        else:
            # The content changed too long after the playback to be related.
            too_late_changes += 1
            change_idx += 1

    # The changes that no playback came before.
    unrelated_changes += len(change_times) - change_idx

    # There is probably a more statistically correct way of doing this but the idea is that
    # with few datapoints we should tend towards 0.5 probability but as we get more datapoints
    # then error goes down and rely on actual changes vs nonchanges
    # We will do a simple weighted average with 0.5 to simulate this
    # TODO: currently random widgets score higher than recently played widgets. need to score them lower
    # as they are less relevent
    # HACK: could too late changes for now until we work out why
    datapoints = float(changed + too_late_changes + non_changes)
    all_changes = float(datapoints + unrelated_changes)
    if all_changes == 0:
        # we have no data or lost it. let's get it updated
        prob = 1.0
    else:
        prob = (changed) / all_changes
        unknown_weight = 4
        prob = (prob * datapoints + 0.5 * unknown_weight) / (
            datapoints + unknown_weight
        )

    utils.log(
        f"prob:{prob * 100:.2f}% changes:{changed} non_changes:{non_changes} non_play_changes:{unrelated_changes} too_late:{too_late_changes} plays:{len(plays)} hist:{hist_len}: {path}",
        "notice",
    )
    return prob


def save_playback_history(media_type, playback_percentage, path):
    # Record in json when things got played to help predict which widgets will change after playback
    # if playback_percentage < 0.7:
    #    return
    history = utils.read_json(_playback_history_path, default={})
    plays = history.setdefault("plays", [])
    plays.append((time.time(), media_type))
    if len(plays) > MAX_HISTORY_ENTRIES:
        del plays[:-MAX_HISTORY_ENTRIES]
    utils.write_json(_playback_history_path, history)
