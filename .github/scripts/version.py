#!/usr/bin/env python3
"""Version helpers shared by the build scripts and the workflows.

Kodi compares add-on versions as dotted numbers with an optional pre-release
suffix, for example ``1.0.0`` or ``1.0.0~beta1``.  A semver style suffix
(``1.0.0-beta1``) is therefore normalised to the Kodi notation.

Usage::

    python3 version.py 1.0.0-beta1          # prints 1.0.0~beta1
    python3 version.py --prerelease 1.0.0   # prints false
"""

from __future__ import annotations

import argparse
import re
import sys

VERSION_PATTERN = re.compile(r"^[0-9]+(\.[0-9]+)*(~[0-9A-Za-z.\-]+)?$")
PRERELEASE_PATTERN = re.compile(r"^[0-9]+(\.[0-9]+)*~")


def normalize_version(requested: str) -> str:
    version = (requested or "").strip()
    if version.startswith("v"):
        version = version[1:]
    if not version:
        raise SystemExit("A version is required")
    version = version.replace("-", "~", 1)
    if not VERSION_PATTERN.match(version):
        raise SystemExit(
            f"Invalid version {version!r}: Kodi expects a dotted version like 1.0.0"
        )
    return version


def is_prerelease(version: str) -> bool:
    return bool(PRERELEASE_PATTERN.match(version))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prerelease", action="store_true", help="Print true for a pre-release")
    parser.add_argument("version", help="The version to inspect")
    args = parser.parse_args()

    version = normalize_version(args.version)
    if args.prerelease:
        print("true" if is_prerelease(version) else "false")
    else:
        print(version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
