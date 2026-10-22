"""Tests for the layout of the add-on settings.

Kodi has four levels, basic, standard, advanced and expert.  The settings
that can destroy the groups of the user belong to the expert level, the
ones a user changes once belong to the basic level.
"""

import os
import xml.etree.ElementTree as ET

ADDON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "plugin.program.autowidget",
)

SETTINGS = os.path.join(ADDON, "resources", "settings.xml")

# The settings that destroy the groups or the widgets of the user.
DESTRUCTIVE = ("30042",)


def _parse():
    root = ET.parse(SETTINGS).getroot()
    settings = {}
    for category in root.findall("category"):
        for setting in category.findall("setting"):
            label = setting.get("label", "")
            if label:
                settings[label] = setting
    return root, settings


def _find(settings, string_id):
    for label, setting in settings.items():
        if label.endswith(f"{string_id}]"):
            return setting
    raise AssertionError(f"{string_id} is not in the settings")


def test_the_settings_have_a_level():
    _root, settings = _parse()

    for label, setting in settings.items():
        level = setting.get("level")
        assert level is not None, f"{label} has no level"
        assert level in ("0", "1", "2", "3"), f"{label} has the level {level}"


def test_the_destructive_settings_are_for_the_expert():
    _root, settings = _parse()

    for string_id in DESTRUCTIVE:
        setting = _find(settings, string_id)
        assert setting.get("level") == "3", f"{string_id} is not for the expert"


def test_the_categories_are_the_ones_we_expect():
    root, _settings = _parse()

    labels = [category.get("label") for category in root.findall("category")]

    assert labels == [
        "$ADDON[plugin.program.autowidget 30177]",  # Widgets
        "$ADDON[plugin.program.autowidget 30178]",  # Service
        "$ADDON[plugin.program.autowidget 30123]",  # Icons
        "$ADDON[plugin.program.autowidget 30008]",  # Tools
    ]


def test_the_service_settings_are_in_the_basic_level():
    _root, settings = _parse()

    assert _find(settings, "30025").get("level") == "0"
    assert _find(settings, "30005").get("level") == "0"


def test_the_settings_are_valid_xml():
    """The action urls hold an ampersand, it has to be escaped."""
    root = ET.parse(SETTINGS).getroot()

    assert root.tag == "settings"
