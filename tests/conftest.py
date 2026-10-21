"""Shared test setup.

The mocked Kodi modules have to be in place before any add-on module is
imported, since those import ``xbmc`` and friends at module level.
"""

import os
import sys

import pytest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(TESTS_DIR)
ADDON_DIR = os.path.join(REPO_DIR, "plugin.program.autowidget")

sys.path.insert(0, TESTS_DIR)
sys.path.insert(0, ADDON_DIR)

import kodi_mock  # noqa: E402

# One mock for the whole test session, the add-on reads its profile
# path at import time.
mock = kodi_mock.KodiMock()
mock.install()


@pytest.fixture
def kodi():
    """The mocked Kodi environment."""
    return mock


def pytest_unconfigure(config):
    mock.cleanup()
