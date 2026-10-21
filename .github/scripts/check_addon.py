#!/usr/bin/env python3
"""Validate the AutoWidget add-on before it is built or published.

The checks mirror the resource validation that a Kodi add-on needs to pass:

* ``addon.xml`` must be well formed and carry the expected metadata
* every ``$ADDON[plugin.program.autowidget NNNNN]`` reference (and every
  ``lvalues`` id) must exist in the English string table
* every language directory must provide a ``strings.po`` file
* all Python sources must compile
"""

from __future__ import annotations

import argparse
import compileall
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ADDON_ID = "plugin.program.autowidget"
REFERENCE_PATTERNS = (
    re.compile(r"\$ADDON\[" + re.escape(ADDON_ID) + r"\s+(\d+)\]"),
    re.compile(r"\$LOCALIZE\[(\d+)\]"),
)
LVALUES_PATTERN = re.compile(r'\blvalues="([0-9|]+)"')
PO_CONTEXT_PATTERN = re.compile(r'^msgctxt\s+"#(\d+)"', re.MULTILINE)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def parse_po_contexts(path: Path) -> set[str]:
    content = path.read_text(encoding="utf-8", errors="replace")
    return set(PO_CONTEXT_PATTERN.findall(content))


def check_addon_xml(addon_xml: Path, report: Report) -> ET.Element:
    try:
        tree = ET.parse(addon_xml)
    except ET.ParseError as error:
        report.error(f"{addon_xml}: invalid XML: {error}")
        return ET.Element("addon")

    root = tree.getroot()
    for attribute in ("id", "name", "version", "provider-name"):
        if not root.get(attribute):
            report.error(f"{addon_xml}: missing required attribute {attribute!r}")
    if root.get("id") != ADDON_ID:
        report.error(f"{addon_xml}: unexpected add-on id {root.get('id')!r}")
    if not root.findall("extension"):
        report.error(f"{addon_xml}: no extension points declared")
    return root


def collect_references(addon_dir: Path) -> dict[str, list[str]]:
    references: dict[str, list[str]] = {}
    candidates = list(addon_dir.rglob("*.py")) + list(addon_dir.rglob("*.xml"))
    for path in candidates:
        if "language" in path.parts:
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        found: set[str] = set()
        for pattern in REFERENCE_PATTERNS:
            found.update(pattern.findall(content))
        for group in LVALUES_PATTERN.findall(content):
            found.update(value for value in group.split("|") if value)
        if found:
            references[str(path)] = sorted(found)
    return references


def check_strings(addon_dir: Path, report: Report) -> None:
    language_dir = addon_dir / "resources" / "language"
    if not language_dir.is_dir():
        report.error(f"Missing language directory: {language_dir}")
        return

    reference_po = language_dir / "resource.language.en_gb" / "strings.po"
    if not reference_po.is_file():
        report.error(f"Missing reference string table: {reference_po}")
        return

    known = parse_po_contexts(reference_po)
    if not known:
        report.error(f"{reference_po}: no string ids found")
        return

    for source, ids in collect_references(addon_dir).items():
        for string_id in ids:
            if string_id not in known:
                report.error(
                    f"{source}: references string #{string_id} which is missing "
                    f"from {reference_po.name}"
                )

    for po_file in sorted(language_dir.glob("resource.language.*/strings.po")):
        if po_file == reference_po:
            continue
        missing = known - parse_po_contexts(po_file)
        if missing:
            report.warn(
                f"{po_file}: {len(missing)} string(s) missing: "
                f"{', '.join('#' + item for item in sorted(missing)[:10])}"
            )


def check_compilation(addon_dir: Path, report: Report) -> None:
    ok = compileall.compile_dir(
        str(addon_dir), quiet=2, force=True, legacy=False, workers=0
    )
    if not ok:
        report.error(f"Python sources in {addon_dir} failed to compile")


def check_zip(zip_path: Path, expected_version: str | None, report: Report) -> None:
    """Validate a built add-on zip the way Kodi consumes it."""
    import zipfile

    if not zip_path.is_file():
        report.error(f"Add-on zip not found: {zip_path}")
        return

    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        roots = {name.split("/")[0] for name in names}
        if len(roots) != 1:
            report.error(f"{zip_path}: the zip must contain a single add-on folder, got {roots}")
            return

        root = roots.pop()

        addon_xml_name = f"{root}/addon.xml"
        if addon_xml_name not in names:
            report.error(f"{zip_path}: addon.xml is missing")
            return

        addon_xml = ET.fromstring(archive.read(addon_xml_name))
        if addon_xml.get("id") != root:
            report.error(
                f"{zip_path}: the folder name {root!r} does not match the add-on id "
                f"{addon_xml.get('id')!r}"
            )

        version = addon_xml.get("version") or ""
        if expected_version and version != expected_version:
            report.error(
                f"{zip_path}: the version in addon.xml is {version!r}, expected {expected_version!r}"
            )
        if version == "CURRENT_VERSION":
            report.error(f"{zip_path}: the version placeholder was not replaced")

        if root == ADDON_ID:
            required_assets = ("resources/media/icon.png", "resources/media/fanart.png")
        else:
            required_assets = ("icon.png",)
        for asset in required_assets:
            if f"{root}/{asset}" not in names:
                report.error(f"{zip_path}: missing {asset}")

        for name in names:
            if name.endswith("/") or "__pycache__" in name or name.endswith(".pyc"):
                report.error(f"{zip_path}: unexpected file {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--addon-path",
        default=str(Path(__file__).resolve().parents[2] / ADDON_ID),
        help="Path to the add-on source directory",
    )
    parser.add_argument("--zip", help="Also validate a built add-on zip")
    parser.add_argument("--version", help="Version expected inside the built zip")
    args = parser.parse_args()

    addon_dir = Path(args.addon_path)
    report = Report()

    if not addon_dir.is_dir():
        report.error(f"Add-on directory not found: {addon_dir}")
    else:
        check_addon_xml(addon_dir / "addon.xml", report)
        check_strings(addon_dir, report)
        check_compilation(addon_dir, report)

    if args.zip:
        check_zip(Path(args.zip), args.version, report)

    for warning in report.warnings:
        print(f"warning: {warning}")
    for error in report.errors:
        print(f"error: {error}")

    if report.errors:
        print(f"Check failed with {len(report.errors)} error(s)")
        return 1

    print("All checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
