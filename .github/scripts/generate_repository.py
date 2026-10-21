#!/usr/bin/env python3
"""Build a Kodi add-on repository from a built add-on zip.

The layout follows the Kodi wiki (https://kodi.wiki/view/Add-on_repositories):

    addons.xml                 index of every add-on in the repository
    addons.xml.md5             checksum of addons.xml
    <addon.id>/
        <addon.id>-<version>.zip
        <addon.id>-<version>.zip.md5
        icon.png, fanart.png, ...   the assets of the add-on
        changelog-<version>.txt

Kodi downloads the add-on zip from ``<datadir>/<addon.id>/<addon.id>-<version>.zip``,
so the folder per add-on id is mandatory.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

SKIPPED_TAGS = {"news", "reuselanguageinvoker"}
ASSET_FILES = {
    "icon.png": "resources/media/icon.png",
    "fanart.png": "resources/media/fanart.png",
    "poster.png": "resources/media/poster.png",
    "banner.png": "resources/media/banner.png",
    "clearlogo.png": "resources/media/clearlogo.png",
}


def build_addons_xml(addon: ET.Element, version: str) -> str:
    if addon.tag != "addon":
        raise SystemExit(f"Unexpected root element: {addon.tag}")

    addon = copy.deepcopy(addon)
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


def extract_changelog(addon: ET.Element, version: str) -> str:
    news = addon.find(".//news")
    if news is None:
        return f"AutoWidget {version}\n"

    text = (news.text or "").strip("\n")
    lines = [line.rstrip() for line in text.splitlines()]
    changelog: list[str] = []
    for line in lines:
        if re.match(r"^\d+(\.\d+)*", line.strip()):
            if changelog:
                break
            changelog.append(f"AutoWidget {version}")
            continue
        changelog.append(line)

    if not changelog:
        changelog = [f"AutoWidget {version}"]
    return "\n".join(changelog).strip() + "\n"


def copy_assets(archive: zipfile.ZipFile, addon_id: str, target: Path) -> None:
    names = set(archive.namelist())
    for target_name, source in ASSET_FILES.items():
        source = f"{addon_id}/{source}"
        if source in names:
            with archive.open(source) as handle, open(target / target_name, "wb") as out:
                shutil.copyfileobj(handle, out)


def build_repository(addon_zip: Path, version: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(addon_zip) as archive:
        addon_xml_name = next(
            (name for name in archive.namelist() if name.endswith("/addon.xml")), None
        )
        if addon_xml_name is None:
            raise SystemExit(f"{addon_zip}: no addon.xml found in the add-on zip")
        addon_id = addon_xml_name.split("/")[0]

        addon = ET.fromstring(archive.read(addon_xml_name))
        if addon.get("id") != addon_id:
            raise SystemExit(
                f"{addon_zip}: the folder name {addon_id!r} does not match the add-on id "
                f"{addon.get('id')!r}"
            )

        addons_xml = build_addons_xml(addon, version)
        (output_dir / "addons.xml").write_text(addons_xml, encoding="utf-8")
        (output_dir / "addons.xml.md5").write_text(
            hashlib.md5(addons_xml.encode("utf-8")).hexdigest(), encoding="utf-8"
        )

        addon_dir = output_dir / addon_id
        addon_dir.mkdir(parents=True, exist_ok=True)

        zip_name = f"{addon_id}-{version}.zip"
        shutil.copyfile(addon_zip, addon_dir / zip_name)
        (addon_dir / f"{zip_name}.md5").write_text(
            hashlib.md5(addon_zip.read_bytes()).hexdigest(), encoding="utf-8"
        )

        copy_assets(archive, addon_id, addon_dir)

        changelog = extract_changelog(addon, version)
        (addon_dir / f"changelog-{version}.txt").write_text(changelog, encoding="utf-8")

    print(f"Generated repository in {output_dir}")
    return output_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="Version of the published add-on")
    parser.add_argument("--addon-zip", required=True, help="Path to the built add-on zip")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory the repository files are written to",
    )
    args = parser.parse_args()

    build_repository(Path(args.addon_zip), args.version, Path(args.output_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
