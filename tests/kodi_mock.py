"""A minimal mock of the Kodi Python API.

Kodi's Python modules only exist inside Kodi itself, so the add-on is
exercised against this mock instead. The mock keeps just enough state
to be able to drive the add-on: info labels, JSON-RPC responses, add-on
settings, a virtual file system and the directory items that were
handed over to Kodi.
"""

import json
import os
import shutil
import sys
import tempfile
import types


class MockListItem(object):
    """Records what the add-on sets on a list item."""

    def __init__(self, label="", label2="", path="", offscreen=False):
        self.label = label
        self.label2 = label2
        self.path = path
        self.info = {}
        self.art = {}
        self.properties = {}
        self.uniqueids = {}
        self.cast = None
        self.mimetype = None
        self.stream_info = []

    def setInfo(self, type, infoLabels):
        self.info.setdefault(type, {}).update(infoLabels)

    def setArt(self, dictionary):
        self.art.update(dictionary)

    def setProperty(self, key, value):
        self.properties[key] = value

    def getProperty(self, key):
        return self.properties.get(key, "")

    def setUniqueIDs(self, values):
        self.uniqueids.update(values)

    def setCast(self, actors):
        self.cast = actors

    def setMimeType(self, mimetype):
        self.mimetype = mimetype

    def addStreamInfo(self, type, values):
        self.stream_info.append((type, values))

    def addContextMenuItems(self, items, replaceItems=False):
        pass

    def __repr__(self):
        return "<MockListItem {!r}>".format(self.label)


class MockDialog(object):
    def __init__(self, mock):
        self._mock = mock

    def yesno(self, *args, **kwargs):
        return self._mock.dialog_answers.get("yesno", True)

    def notification(self, *args, **kwargs):
        self._mock.notifications.append(args)

    def input(self, *args, **kwargs):
        return self._mock.dialog_answers.get("input", "")

    def select(self, *args, **kwargs):
        return self._mock.dialog_answers.get("select", -1)

    def multiselect(self, *args, **kwargs):
        return self._mock.dialog_answers.get("multiselect", None)

    def browse(self, *args, **kwargs):
        return self._mock.dialog_answers.get("browse", "")


class MockDialogProgress(object):
    def __init__(self, *args, **kwargs):
        self.updates = []

    def create(self, *args, **kwargs):
        pass

    def update(self, percent, message=""):
        self.updates.append((percent, message))

    def close(self):
        pass


class KodiMock(object):
    """Installs fake ``xbmc`` modules into ``sys.modules``."""

    def __init__(self, profile=None):
        self.profile = profile or tempfile.mkdtemp(prefix="autowidget-test-")
        self.home = os.path.join(self.profile, "home")
        self.addons = os.path.join(self.home, "addons")
        os.makedirs(self.addons, exist_ok=True)

        self.info_labels = {}
        self.conditions = {}
        self.logged = []
        self.directory_items = []
        self.properties = {}
        self.notifications = []
        self.dialog_answers = {}
        self.addon_settings = {}
        self.addon_info = {}
        self.jsonrpc_handler = None
        self.modules = {}

    # -- helpers --------------------------------------------------------
    def set_info_label(self, label, value):
        self.info_labels[label] = value

    def set_jsonrpc_handler(self, handler):
        """handler(request_dict) -> response dict (or str)"""
        self.jsonrpc_handler = handler

    def translate_path(self, path):
        if path.startswith("special://profile"):
            return os.path.join(self.profile, path[len("special://profile"):].lstrip("/"))
        if path.startswith("special://home"):
            return os.path.join(self.home, path[len("special://home"):].lstrip("/"))
        if path.startswith("special://masterprofile"):
            return os.path.join(self.home, path[len("special://masterprofile"):].lstrip("/"))
        if path.startswith("special://"):
            return os.path.join(self.home, path[len("special://"):].lstrip("/"))
        return path

    def cleanup(self):
        for name in self.modules:
            sys.modules.pop(name, None)
        shutil.rmtree(self.profile, ignore_errors=True)

    # -- module factory -------------------------------------------------
    def _build_xbmc(self):
        xbmc = types.ModuleType("xbmc")
        xbmc.LOGDEBUG = 0
        xbmc.LOGINFO = 1
        xbmc.LOGWARNING = 2
        xbmc.LOGERROR = 3
        xbmc.LOGFATAL = 4
        xbmc.LOGNONE = 5

        mock = self

        def getInfoLabel(label):
            return mock.info_labels.get(label, "")

        def getInfoImage(label):
            return mock.info_labels.get(label, "")

        def getCondVisibility(condition):
            return mock.conditions.get(condition, False)

        def getAppInfo(label):
            return mock.addon_info.get(label, "")

        def log(msg, level=xbmc.LOGDEBUG):
            mock.logged.append((msg, level))

        def sleep(ms):
            pass

        def executebuiltin(command, wait=False):
            pass

        def executeJSONRPC(request):
            if isinstance(request, (str, bytes)):
                request = json.loads(request)
            if mock.jsonrpc_handler is None:
                return json.dumps({"jsonrpc": "2.0", "id": request.get("id"), "result": {}})
            response = mock.jsonrpc_handler(request)
            if isinstance(response, str):
                return response
            return json.dumps(response)

        class Monitor(object):
            def __init__(self, *args, **kwargs):
                pass

            def waitForAbort(self, timeout=0):
                return False

            def abortRequested(self):
                return False

        class Player(object):
            def __init__(self, *args, **kwargs):
                pass

            def isPlaying(self):
                return False

            def isPlayingVideo(self):
                return False

            def isPlayingAudio(self):
                return False

            def getPlayingFile(self):
                return ""

            def getTotalTime(self):
                return 0.0

            def getTime(self):
                return 0.0

        xbmc.getInfoLabel = getInfoLabel
        xbmc.getInfoImage = getInfoImage
        xbmc.getCondVisibility = getCondVisibility
        xbmc.getAppInfo = getAppInfo
        xbmc.log = log
        xbmc.sleep = sleep
        xbmc.executebuiltin = executebuiltin
        xbmc.executeJSONRPC = executeJSONRPC
        xbmc.Monitor = Monitor
        xbmc.Player = Player
        xbmc.translatePath = self.translate_path
        return xbmc

    def _build_xbmcaddon(self):
        xbmcaddon = types.ModuleType("xbmcaddon")
        mock = self

        class Addon(object):
            def __init__(self, id=None):
                self.id = id or "plugin.program.autowidget"
                self._settings = mock.addon_settings.setdefault(self.id, {})

            def getAddonInfo(self, label):
                info = {
                    "id": self.id,
                    "name": "AutoWidget",
                    "version": "3.8.0",
                    "path": mock.addon_info.get("path", ""),
                    "profile": mock.profile,
                    "type": "xbmc.python.pluginsource",
                }
                return info.get(label, "")

            def getLocalizedString(self, id):
                return "string-{}".format(id)

            def getSetting(self, key):
                return self._settings.get(key, "")

            def getSettingBool(self, key):
                return bool(self._settings.get(key, False))

            def getSettingInt(self, key):
                return int(self._settings.get(key, 0) or 0)

            def getSettingNumber(self, key):
                return float(self._settings.get(key, 0) or 0)

            def getSettingString(self, key):
                return str(self._settings.get(key, ""))

            def setSetting(self, key, value):
                self._settings[key] = value
                return True

            def setSettingBool(self, key, value):
                self._settings[key] = value
                return True

            def setSettingInt(self, key, value):
                self._settings[key] = value
                return True

            def setSettingNumber(self, key, value):
                self._settings[key] = value
                return True

            def setSettingString(self, key, value):
                self._settings[key] = value
                return True

        xbmcaddon.Addon = Addon
        return xbmcaddon

    def _build_xbmcgui(self):
        xbmcgui = types.ModuleType("xbmcgui")
        mock = self

        class ListItem(MockListItem):
            pass

        class Window(object):
            def __init__(self, windowId=-1):
                self.windowId = windowId

            def setProperty(self, key, value):
                mock.properties[key] = value

            def getProperty(self, key):
                return mock.properties.get(key, "")

            def clearProperty(self, key):
                mock.properties.pop(key, None)

        xbmcgui.ListItem = ListItem
        xbmcgui.Window = Window
        xbmcgui.Dialog = lambda *a, **k: MockDialog(mock)
        xbmcgui.DialogProgress = MockDialogProgress
        xbmcgui.DialogProgressBG = MockDialogProgress
        return xbmcgui

    def _build_xbmcvfs(self):
        xbmcvfs = types.ModuleType("xbmcvfs")
        mock = self

        def translatePath(path):
            return mock.translate_path(path)

        def exists(path):
            return os.path.exists(path)

        def mkdirs(path):
            os.makedirs(path, exist_ok=True)

        def mkdir(path):
            os.makedirs(path, exist_ok=True)

        def rmdir(path, force=False):
            shutil.rmtree(path, ignore_errors=True)

        def listdir(path):
            if not os.path.isdir(path):
                return ([], [])
            dirs, files = [], []
            for entry in sorted(os.listdir(path)):
                if os.path.isdir(os.path.join(path, entry)):
                    dirs.append(entry)
                else:
                    files.append(entry)
            return (dirs, files)

        def delete(path):
            os.remove(path)

        def copy(src, dst):
            shutil.copyfile(src, dst)

        class File(object):
            def __init__(self, path, mode="r"):
                self.path = path
                self.mode = mode
                self._file = open(path, mode if "b" in mode else mode + "b")

            def read(self):
                return self._file.read()

            def readBytes(self):
                return self._file.read()

            def write(self, content):
                return self._file.write(content)

            def close(self):
                self._file.close()

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.close()

        class Stat(object):
            def __init__(self, path):
                self._stat = os.stat(path)

            def st_size(self):
                return self._stat.st_size

            def st_mtime(self):
                return self._stat.st_mtime

        xbmcvfs.translatePath = translatePath
        xbmcvfs.exists = exists
        xbmcvfs.mkdirs = mkdirs
        xbmcvfs.mkdir = mkdir
        xbmcvfs.rmdir = rmdir
        xbmcvfs.listdir = listdir
        xbmcvfs.delete = delete
        xbmcvfs.copy = copy
        xbmcvfs.File = File
        xbmcvfs.Stat = Stat
        return xbmcvfs

    def _build_xbmcplugin(self):
        xbmcplugin = types.ModuleType("xbmcplugin")
        mock = self

        xbmcplugin.SORT_METHOD_UNSORTED = 0
        xbmcplugin.SORT_METHOD_LABEL = 1
        xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE = 2
        xbmcplugin.SORT_METHOD_DATE = 3
        xbmcplugin.SORT_METHOD_TITLE = 4
        xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE = 5
        xbmcplugin.SORT_METHOD_LASTPLAYED = 6

        def addDirectoryItem(handle, url, listitem=None, isFolder=False, totalItems=0):
            mock.directory_items.append((url, listitem, isFolder))

        def addSortMethod(handle, sortMethod, label2Mask=""):
            pass

        def setContent(handle, content):
            pass

        def setPluginCategory(handle, category):
            pass

        def endOfDirectory(handle, succeeded=True, updateListing=False, cacheToDisc=True):
            pass

        xbmcplugin.addDirectoryItem = addDirectoryItem
        xbmcplugin.addSortMethod = addSortMethod
        xbmcplugin.setContent = setContent
        xbmcplugin.setPluginCategory = setPluginCategory
        xbmcplugin.endOfDirectory = endOfDirectory
        return xbmcplugin

    # -- installation ---------------------------------------------------
    def install(self):
        """Register the mocked Kodi modules in ``sys.modules``."""
        self.modules = {
            "xbmc": self._build_xbmc(),
            "xbmcaddon": self._build_xbmcaddon(),
            "xbmcgui": self._build_xbmcgui(),
            "xbmcvfs": self._build_xbmcvfs(),
            "xbmcplugin": self._build_xbmcplugin(),
        }
        sys.modules.update(self.modules)
        return self
