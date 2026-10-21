import re

import xbmc

# Codename of the Kodi releases we know about, by major version.
KODI_CODENAMES = {
    19: "Matrix",
    20: "Nexus",
    21: "Omega",
    22: "Piers",
}

_version = None


def get_build_version():
    """Raw build version of the running Kodi.

    e.g. "21.3 (21.3.0) Git:20251031-1f2e3d4c5b6"
    """
    try:
        return xbmc.getInfoLabel("System.BuildVersion") or ""
    except Exception:
        return ""


def get_version():
    """(major, minor) version tuple of the running Kodi, e.g. (21, 3).

    Returns (0, 0) when the version can't be determined.
    """
    global _version

    if _version is None:
        match = re.search(r"(\d+)\.(\d+)", get_build_version())
        _version = (int(match.group(1)), int(match.group(2))) if match else (0, 0)

    return _version


def get_version_string():
    """Human readable version of the running Kodi, e.g. "21.3 (Omega)"."""
    major, minor = get_version()

    if major == 0:
        return "unknown"

    codename = KODI_CODENAMES.get(major)
    if codename:
        return f"{major}.{minor} ({codename})"

    return f"{major}.{minor}"


def at_least(major, minor=0):
    """True when the running Kodi is at least the given version."""
    current_major, current_minor = get_version()

    if current_major == 0:
        return False

    return (current_major, current_minor) >= (major, minor)
