#!/usr/bin/env python3
"""Stamp the released version into the add-on source.

The release workflow builds the add-on zip with the version of the release and
commits the updated ``addon.xml`` back to the repository, so the source always
carries the version of the latest release.  The changelog of the release is
added to the ``news`` element of the add-on, which Kodi shows in the add-on
information dialog.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from version import normalize_version  # noqa: E402

VERSION_PATTERN = re.compile(r'(<addon\b[^>]*?\bversion=")([^"]*)(")')
NEWS_PATTERN = re.compile(r"(<news>)")
CHANGELOG_HEADING = re.compile(r"^##\s+(?:\[)?(?P<version>[^\]\s]+)")
BULLET = re.compile(r"^(\s*)[-*]\s+(.*)$")
SECTION = re.compile(r"^###\s+(.*)$")


def read_release_notes(changelog: Path) -> list[str]:
    """Return the notes of the newest section of the changelog."""
    if not changelog.is_file():
        return []

    lines = changelog.read_text(encoding="utf-8").splitlines()
    notes: list[str] = []
    started = False

    for line in lines:
        if not started:
            if CHANGELOG_HEADING.match(line):
                started = True
            continue

        if line.startswith("## "):
            break

        section = SECTION.match(line)
        if section:
            title = section.group(1).strip()
            if notes:
                notes.append("")
            notes.append(title)
            continue

        bullet = BULLET.match(line)
        if bullet:
            notes.append(f"  - {bullet.group(2).strip()}")

    return notes


def format_news(version: str, notes: list[str]) -> str:
    block = [version]
    block.extend(notes)
    return "\n".join(block)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--addon-xml", required=True, help="Path to the add-on's addon.xml")
    parser.add_argument("--version", required=True, help="The version of the release")
    parser.add_argument("--changelog", help="Path to CHANGELOG.md")
    args = parser.parse_args()

    version = normalize_version(args.version)
    addon_xml = Path(args.addon_xml)
    content = addon_xml.read_text(encoding="utf-8")

    if not VERSION_PATTERN.search(content):
        raise SystemExit(f"{addon_xml}: no version attribute found")
    content = VERSION_PATTERN.sub(rf"\g<1>{version}\g<3>", content, count=1)

    notes = read_release_notes(Path(args.changelog)) if args.changelog else []
    if notes:
        news = format_news(version, notes)
        content, count = NEWS_PATTERN.subn(
            lambda match: f"{match.group(1)}\n{news}\n", content, count=1
        )
        if not count:
            raise SystemExit(f"{addon_xml}: no news element found")

    addon_xml.write_text(content, encoding="utf-8")
    print(f"Updated {addon_xml} to version {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
