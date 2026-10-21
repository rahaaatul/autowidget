from resources.lib import manage


def test_get_path_by_id_returns_the_path(monkeypatch):
    paths = [{"id": "1", "label": "Movies", "file": {"file": "plugin://movies/"}}]
    monkeypatch.setattr(manage, "find_defined_paths", lambda group_id=None: paths)
    assert manage.get_path_by_id("1", "group")["label"] == "Movies"


def test_get_path_by_id_of_an_unknown_path(monkeypatch):
    # A widget can point at a path that was removed in the meantime,
    # this must not raise.
    monkeypatch.setattr(manage, "find_defined_paths", lambda group_id=None: [])
    assert manage.get_path_by_id("does-not-exist", "group") == {}


def test_get_path_by_id_without_an_id():
    assert manage.get_path_by_id("", "group") == {}
    assert manage.get_path_by_id(None, "group") == {}
