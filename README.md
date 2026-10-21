# AutoWidget

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/840a4c0ed72e4d25b3d82c984e3c4b84)](https://app.codacy.com/manual/drinfernoo/plugin.program.autowidget?utm_source=github.com&utm_medium=referral&utm_content=drinfernoo/plugin.program.autowidget&utm_campaign=Badge_Grade_Dashboard)
[![Build pull request](https://github.com/drinfernoo/plugin.program.autowidget/actions/workflows/build_pull_request.yml/badge.svg)](https://github.com/drinfernoo/plugin.program.autowidget/actions/workflows/build_pull_request.yml)

AutoWidget is a program add-on for Kodi, designed to give a more dynamic and interesting experience to using skin widgets.

See the [Kodi forum post](https://forum.kodi.tv/showthread.php?tid=352934) for more information.

## Kodi Compatibility
---
AutoWidget targets the latest stable Kodi release:

* Kodi 21 "Omega" (21.3 or later)

Older releases are not supported. The add-on uses the Kodi Python 3 API (`xbmc.python` 3.0.1), no longer depends on `six` and uses the Pillow version provided by Kodi.

## Steps to Install
---
1.  Go to the Kodi file manager.
2.  Click on "Add source".
3.  The path for the source is `https://drinfernoo.github.io/` (Give it the name "drinfernoo").
4.  Go to "Add-ons", and choose "Install from zip".
5.  a.  For AutoWidget's Stable repo, install `repository.autowidget-1.1.zip`.
    b.  For AutoWidget's Dev repo (for testing purposes **only**), install `repository.autowidget.dev-1.1.zip`.
6.  Return to "Add-ons", and choose "Install from repository".
7.  Choose the repository you installed (stable or dev), and install AutoWidget from Program Add-ons.

## How to Use
---
To get started using AutoWidget, open the Kodi context menu on any other menu inside Kodi, like the "Popular" menu from your favorite add-on, or the "Movies -> Titles" section of your video library, and choose `Add to AutoWidget Group`. Follow the prompts to add a new path, and then use your skin of choice to set up a widget directed at the group you created. Reload your skin, and you should have a fresh, shiny new AutoWidget!

A group can hold more than one list ("path"). In your skin, point a widget at `Add-ons > AutoWidgets > My Groups > {group} > {group mode}`:

* **Static** shows one path of the group, you pick which one.
* **Cycling** periodically moves to another path of the group, either the next one or a random one. The interval is set in the add-on settings.
* **Merged** combines all paths of the group into a single list.

To add a whole folder of lists to a group at once, use `Add to AutoWidget Group > Explode menu to Group`.

For a more detailed guide, check out [the wiki](https://github.com/drinfernoo/plugin.program.autowidget/wiki/How-to-Use-AutoWidget)!

## YouTube Playlist
---
There is a playlist on YouTube where I keep all of my videos dedicated to AutoWidget. If the tutorial above isn't helping, you'd like to find some of the other features, or just want to see the add-on in action, [check it out on YouTube](https://youtube.com/playlist?list=PLqaI8oSksiy9Y75qF2ALziRPQsv0UrYCz)!

## Development
---
The add-on is a pure Python project, no build system or external dependencies are required. A Python 3.10+ interpreter is enough to build and validate it locally:

```bash
# Install the test requirements
pip install -r tests/requirements.txt

# Run the test suite
python -m pytest tests

# Validate addon.xml, string references and Python sources
python3 .github/scripts/check_addon.py

# Build the installable zip (the version is stamped into addon.xml)
python3 .github/scripts/build_addon.py --version 3.9.0 --output-dir dist
```

The version in `plugin.program.autowidget/addon.xml` is kept as the `CURRENT_VERSION` placeholder. It is replaced with the release version while packaging, so a released artifact always matches its tag.

## Continuous Integration
---
Builds and releases are automated with GitHub Actions (`.github/workflows`):

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `build_pull_request.yml` | push to `dev`, pull request to `dev` | Runs the test suite, validates the add-on, builds the zip and uploads it as a workflow artifact |
| `release.yml` | tag `v*` push, manual run | Builds the add-on, creates a GitHub release with the zip attached, attests its provenance, back-merges `main` into `dev` and publishes the Kodi repository index to the `repo` branch |
| `open_pull_request.yml` | push to `dev` | Opens a draft pull request from `dev` to `main` |

The published add-on zip and the generated repository index (`addons.xml`, `addons.xml.md5`) are pushed to the `repo` branch, which is the location the `repository.autowidget` add-on points at. The CircleCI configuration in `.circleci/config.yml` still runs the test suite and the build; its release job is superseded by the `release.yml` workflow because it references branches and a `create_repository.py` script that no longer exist in this repository.


