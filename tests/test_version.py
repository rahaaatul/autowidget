from resources.lib.common import version


def _reset():
    version._version = None


def test_version_is_parsed_from_the_build_version(monkeypatch):
    _reset()
    monkeypatch.setattr(
        version, "get_build_version", lambda: "21.3 (21.3.0) Git:20251031-1f2e3d4c"
    )
    assert version.get_version() == (21, 3)
    assert version.get_version_string() == "21.3 (Omega)"


def test_version_of_a_newer_release_has_no_codename(monkeypatch):
    _reset()
    monkeypatch.setattr(version, "get_build_version", lambda: "22.0 (22.0.0) Git:1")
    assert version.get_version() == (22, 0)
    assert version.get_version_string() == "22.0 (Piers)"


def test_unknown_build_version(monkeypatch):
    _reset()
    monkeypatch.setattr(version, "get_build_version", lambda: "")
    assert version.get_version() == (0, 0)
    assert version.get_version_string() == "unknown"
    assert version.at_least(19, 0) is False


def test_at_least(monkeypatch):
    _reset()
    monkeypatch.setattr(
        version, "get_build_version", lambda: "21.3 (21.3.0) Git:20251031-1f2e3d4c"
    )
    assert version.at_least(21, 3) is True
    assert version.at_least(21, 0) is True
    assert version.at_least(20, 2) is True
    assert version.at_least(21, 4) is False
    assert version.at_least(22, 0) is False


def test_version_is_cached(monkeypatch):
    _reset()
    calls = []

    def build_version():
        calls.append(1)
        return "21.3 (21.3.0) Git:1"

    monkeypatch.setattr(version, "get_build_version", build_version)
    version.get_version()
    version.get_version()
    assert len(calls) == 1
