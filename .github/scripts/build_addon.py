#!/usr/bin/env python3
"""Build a Kodi add-on zip.

The script stamps the requested version into ``addon.xml`` and packages the
add-on folder into a zip file that Kodi can install directly.  The folder name
and the add-on id are read from ``addon.xml``, so the same script builds the
plugin add-on and the repository add-on.

Kodi expects the version attribute to be a dotted version number such as
``1.0.0``.  Pre-release versions use the ``~`` separator (``1.0.0~beta1``),
so a semver style ``-`` suffix is normalised accordingly.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

VERSION_PLACEHOLDER = "CURRENT_VERSION"
EXCLUDED_DIR_NAMES = {"__pycache__", ".git", ".idea", ".vscode", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
VERSION_PATTERN = re.compile(r"^[0-9]+(\.[0-9]+)*(~[0-9A-Za-z.\-]+)?$")


def resolve_version(requested: str | None) -> str:
    version = (requested or "").strip()
    if version.startswith("v"):
        version = version[1:]
    if not version:
        raise SystemExit("A version is required to build an add-on")
    version = version.replace("-", "~", 1)
    if not VERSION_PATTERN.match(version):
        raise SystemExit(
            f"Invalid version {version!r}: Kodi expects a dotted version like 1.0.0"
        )
    return version


def read_addon_id(addon_xml: Path) -> str:
    try:
        root = ET.parse(addon_xml).getroot()
    except ET.ParseError as error:
        raise SystemExit(f"{addon_xml}: invalid XML: {error}") from error
    addon_id = root.get("id")
    if not addon_id:
        raise SystemExit(f"{addon_xml}: the addon element has no id attribute")
    return addon_id


def set_version(addon_xml: Path, version: str) -> None:
    content = addon_xml.read_text(encoding="utf-8")
    pattern = re.compile(r'(<addon\b[^>]*?\bversion=")([^"]*)(")')
    if not pattern.search(content):
        raise SystemExit(f"{addon_xml}: could not find a version attribute")
    addon_xml.write_text(pattern.sub(rf"\g<1>{version}\g<3>", content, count=1), encoding="utf-8")


def iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        if any(part in EXCLUDED_DIR_NAMES for part in path.parts):
            continue
        if path.suffix in EXCLUDED_SUFFIXES:
            continue
        yield path


def build(addon_path: Path, version: str, output_dir: Path) -> Path:
    if not addon_path.is_dir():
        raise SystemExit(f"Add-on directory not found: {addon_path}")

    addon_xml = addon_path / "addon.xml"
    addon_id = read_addon_id(addon_xml)

    output_dir.mkdir(parents=True, exist_ok=True)
    staging = output_dir / f".staging-{addon_id}"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    target = staging / addon_id
    shutil.copytree(
        addon_path,
        target,
        ignore=shutil.ignore_patterns(*EXCLUDED_DIR_NAMES, "*.pyc", "*.pyo"),
    )
    set_version(target / "addon.xml", version)

    zip_path = output_dir / f"{addon_id}-{version}.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in iter_files(target):
            archive.write(file_path, file_path.relative_to(staging).as_posix())

    shutil.rmtree(staging)
    return zip_path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="Version to stamp into addon.xml")
    parser.add_argument(
        "--addon-path",
        default=str(repo_root / "plugin.program.autowidget"),
        help="Path to the add-on source directory",
    )
    parser.add_argument(
        "--output-dir",
        default=str(repo_root / "dist"),
        help="Directory the zip file is written to",
    )
    args = parser.parse_args()

    version = resolve_version(args.version)
    zip_path = build(Path(args.addon_path), version, Path(args.output_dir))
    print(f"Built {zip_path} (version {version})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
