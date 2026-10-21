#!/usr/bin/env python3
"""Generate the Kodi repository index for a released add-on build.

Kodi repositories are plain zip files containing ``addons.xml`` and
``addons.xml.md5``.  The index is derived from the add-on's own
``addon.xml`` so that the metadata Kodi shows never drifts from the add-on
that is actually shipped.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SKIPPED_TAGS = {"news", "reuselanguageinvoker"}


def build_addons_xml(addon_xml: Path, version: str) -> str:
    tree = ET.parse(addon_xml)
    addon = tree.getroot()

    if addon.tag != "addon":
        raise SystemExit(f"Unexpected root element in {addon_xml}: {addon.tag}")

    addon.set("version", version)

    for parent in addon.iter():
        for child in list(parent):
            if child.tag in SKIPPED_TAGS:
                parent.remove(child)

    root = ET.Element("addons")
    root.append(addon)
    ET.indent(root, space="    ")

    body = ET.tostring(root, encoding="unicode")
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + body + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="Version of the published add-on")
    parser.add_argument(
        "--addon-xml",
        required=True,
        help="Path to the add-on's addon.xml (already stamped with the version)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory addons.xml and addons.xml.md5 are written to",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    addons_xml = build_addons_xml(Path(args.addon_xml), args.version)

    addons_path = output_dir / "addons.xml"
    addons_path.write_text(addons_xml, encoding="utf-8")

    checksum = hashlib.md5(addons_xml.encode("utf-8")).hexdigest()
    (output_dir / "addons.xml.md5").write_text(checksum, encoding="utf-8")

    print(f"Generated {addons_path} and {output_dir / 'addons.xml.md5'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
