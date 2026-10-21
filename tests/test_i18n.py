"""Checks on the shipped translations."""

import os
import re

import pytest

LANGUAGE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "plugin.program.autowidget",
    "resources",
    "language",
)

COLOR_TAG = re.compile(r"\[/?COLOR [a-z]+\]")


def _parse(path):
    """Return {msgctxt id: (msgid, msgstr)} of a Kodi .po file."""
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read().replace("\r\n", "\n")

    entries = {}
    parts = re.split(r'msgctxt "#(\d+)"\n', text)
    for i in range(1, len(parts), 2):
        msg_id = int(parts[i])
        body = parts[i + 1].split("\n#:")[0].split("\nmsgctxt")[0]

        def grab(key):
            match = re.search(key + r'((?:\s*"[^"]*")+)', body)
            if not match:
                return None
            return "".join(re.findall(r'"([^"]*)"', match.group(1)))

        entries[msg_id] = (grab("msgid"), grab("msgstr"))
    return entries


def _languages():
    return sorted(
        name
        for name in os.listdir(LANGUAGE_DIR)
        if os.path.isdir(os.path.join(LANGUAGE_DIR, name))
    )


def _reference():
    return _parse(os.path.join(LANGUAGE_DIR, "resource.language.en_gb", "strings.po"))


LANGUAGES = _languages()


def test_there_are_translations():
    assert len(LANGUAGES) > 1


@pytest.mark.parametrize("language", LANGUAGES)
def test_every_string_is_translated(language):
    reference = _reference()
    entries = _parse(os.path.join(LANGUAGE_DIR, language, "strings.po"))

    missing = sorted(set(reference) - set(entries))
    assert not missing, "missing strings: {}".format(missing)

    untranslated = [
        msg_id
        for msg_id, (msgid, msgstr) in entries.items()
        if not (msgstr or "").strip() and (reference[msg_id][0] or "").strip()
    ]
    assert not untranslated, "untranslated strings: {}".format(untranslated)


@pytest.mark.parametrize("language", LANGUAGES)
def test_no_broken_markup(language):
    reference = _reference()
    entries = _parse(os.path.join(LANGUAGE_DIR, language, "strings.po"))

    for msg_id, (msgid, msgstr) in entries.items():
        if not msgstr:
            continue
        # a truncated placeholder tag breaks the Kodi label
        assert "<ph id=\\" not in msgstr, "#{} has a broken tag".format(msg_id)
        # the french translation of the colour tags used to be translated
        assert "COULEUR]" not in msgstr, "#{} translates a colour tag".format(msg_id)
        # the colour tags of the source string have to be kept
        source = reference.get(msg_id, ("", ""))[0] or ""
        assert msgstr.count("[COLOR ") == source.count("[COLOR "), (
            "#{} lost a colour tag".format(msg_id)
        )
        assert msgstr.count("[/COLOR]") == source.count("[/COLOR]"), (
            "#{} lost a colour tag".format(msg_id)
        )


# Strings that are still shown in english, they are tracked here so that
# the translations don't get worse. Lower the number when a string is
# translated.
UNTRANSLATED = {
    "ar_sa": 5,
    "da_dk": 5,
    "de_de": 11,
    "el_gr": 2,
    "en_gb": 167,
    "en_us": 167,
    "es_es": 2,
    "es_mx": 5,
    "fr_fr": 3,
    "it_it": 11,
    "nl_nl": 6,
    "pt_br": 7,
}


@pytest.mark.parametrize("language", LANGUAGES)
def test_untranslated_strings_do_not_grow(language):
    entries = _parse(os.path.join(LANGUAGE_DIR, language, "strings.po"))
    untranslated = sum(
        1
        for msgid, msgstr in entries.values()
        if msgid
        and msgstr
        and msgstr.strip() == msgid.strip()
        and len(msgid.strip()) > 3
    )
    known = UNTRANSLATED[language.replace("resource.language.", "")]
    assert untranslated <= known, (
        "{} has {} untranslated strings, at most {} are known".format(
            language, untranslated, known
        )
    )
