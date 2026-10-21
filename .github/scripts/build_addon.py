#!/usr/bin/env python3
"""Build the AutoWidget Kodi add-on zip.

The add-on version is kept as the placeholder ``CURRENT_VERSION`` in
``addon.xml`` so that a single source of truth (the release tag) drives the
version of every published artifact.  This script replaces the placeholder with
the requested version and packages the add-on folder into a zip file that Kodi
can install directly.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from pathlib import Path

ADDON_ID = "plugin.program.autowidget"
ADDON_DIR = ADDON_ID
VERSION_PLACEHOLDER = "CURRENT_VERSION"
EXCLUDED_DIR_NAMES = {"__pycache__", ".git", ".idea", ".vscode", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def resolve_version(requested: str | None) -> str:
    if requested:
        version = requested.strip()
    else:
        version = VERSION_PLACEHOLDER
    if version.startswith("v"):
        version = version[1:]
    if not version:
        raise SystemExit("No version given and no fallback available")
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)*(-[0-9A-Za-z.\-]+)?", version):
        raise SystemExit(f"Invalid version: {version!r}")
    return version


def set_version(addon_xml: Path, version: str) -> None:
    content = addon_xml.read_text(encoding="utf-8")
    pattern = re.compile(
        r'(<addon\b[^>]*?\bversion=")' + re.escape(VERSION_PLACEHOLDER) + r'(")',
        re.IGNORECASE,
    )
    if not pattern.search(content):
        raise SystemExit(
            f"Could not find the {VERSION_PLACEHOLDER!r} version placeholder in {addon_xml}"
        )
    addon_xml.write_text(pattern.sub(rf"\g<1>{version}\g<2>", content), encoding="utf-8")


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

    output_dir.mkdir(parents=True, exist_ok=True)
    staging = output_dir / f".staging-{ADDON_DIR}"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    target = staging / ADDON_DIR
    shutil.copytree(
        addon_path,
        target,
        ignore=shutil.ignore_patterns(*EXCLUDED_DIR_NAMES, "*.pyc", "*.pyo"),
    )
    set_version(target / "addon.xml", version)

    zip_path = output_dir / f"{ADDON_ID}-{version}.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in iter_files(target):
            archive.write(file_path, file_path.relative_to(staging).as_posix())

    shutil.rmtree(staging)
    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", help="Version to stamp into addon.xml")
    parser.add_argument(
        "--addon-path",
        default=str(Path(__file__).resolve().parents[2] / ADDON_DIR),
        help="Path to the add-on source directory",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[2] / "dist"),
        help="Directory the zip file is written to",
    )
    args = parser.parse_args()

    version = resolve_version(args.version)
    zip_path = build(Path(args.addon_path), version, Path(args.output_dir))
    print(f"Built {zip_path} (version {version})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
