# AutoWidget

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/840a4c0ed72e4d25b3d82c984e3c4b84)](https://app.codacy.com/manual/rahaaatul/autowidget?utm_source=github.com&utm_medium=referral&utm_content=rahaaatul/autowidget&utm_campaign=Badge_Grade_Dashboard)
[![Build pull request](https://github.com/rahaaatul/autowidget/actions/workflows/build_pull_request.yml/badge.svg)](https://github.com/rahaaatul/autowidget/actions/workflows/build_pull_request.yml)

AutoWidget is a program add-on for Kodi, designed to give a more dynamic and interesting experience to using skin widgets.

See the [Kodi forum post](https://forum.kodi.tv/showthread.php?tid=352934) for more information.

## Kodi Compatibility
---
AutoWidget targets the latest stable Kodi release:

* Kodi 21 "Omega" (21.3 or later)

Older releases are not supported. The add-on uses the Kodi Python 3 API (`xbmc.python` 3.0.1), no longer depends on `six` and uses the Pillow version provided by Kodi.

## Steps to Install
---
1.  Go to the [releases page](https://github.com/rahaaatul/autowidget/releases) and download the latest `plugin.program.autowidget-<version>.zip`.
2.  In Kodi, go to "Add-ons" and choose "Install from zip file".
3.  Select the downloaded `plugin.program.autowidget-<version>.zip`.
4.  AutoWidget is then available in "Add-ons > Program add-ons".

To follow the development versions, install a pre-release from the releases page; pre-releases are marked as such on GitHub.


## How to Use
---
To get started using AutoWidget, open the Kodi context menu on any other menu inside Kodi, like the "Popular" menu from your favorite add-on, or the "Movies -> Titles" section of your video library, and choose `Add to AutoWidget Group`. Follow the prompts to add a new path, and then use your skin of choice to set up a widget directed at the group you created. Reload your skin, and you should have a fresh, shiny new AutoWidget!

A group can hold more than one list ("path"). In your skin, point a widget at `Add-ons > AutoWidgets > My Groups > {group} > {group mode}`:

* **Static** shows one path of the group, you pick which one.
* **Cycling** periodically moves to another path of the group, either the next one or a random one. The interval is set in the add-on settings.
* **Merged** combines all paths of the group into a single list.

A merged widget uses all the paths of its group, the add-on never asks which
ones to use.  To merge only some of them, open the widget in `Add-ons >
AutoWidgets > Active Widgets`, open its context menu and choose `Paths`.

To add a whole folder of lists to a group at once, use `Add to AutoWidget Group > Explode menu to Group`.

For a more detailed guide, check out [the wiki](https://github.com/drinfernoo/plugin.program.autowidget/wiki/How-to-Use-AutoWidget)!

AutoWidget is a fork of [drinfernoo's add-on](https://github.com/drinfernoo/plugin.program.autowidget), which is where the original documentation lives.

## Skin Widgets
---
A skin widget is a small list on the home screen of a skin.  AutoWidget knows when it is rendered inside such a widget and behaves differently: the management actions of the add-on are not useful there and dialogs are intrusive, so they are skipped.

A widget is requested with `widget=true` in the plugin url:

```
plugin://plugin.program.autowidget/?mode=path&group={group}&action=static&widget=true
```

Skins that support the [Skin Shortcuts](https://github.com/MikeSiLVO/script.skinshortcuts) add-on can set the parameter once in the shortcut of the widget.  A skin can also opt in by setting the `AutoWidget.WidgetMode` property on the home window.

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

# Build the installable add-on zip (the version is stamped into addon.xml)
python3 .github/scripts/build_addon.py --version 1.0.0 --addon-path plugin.program.autowidget --output-dir dist

# Check the built zip
python3 .github/scripts/check_addon.py --zip dist/plugin.program.autowidget-1.0.0.zip --version 1.0.0
```

The version in `plugin.program.autowidget/addon.xml` is the version of the latest release. The release workflow builds the zip with the version of the release and commits the updated `addon.xml` back to the repository, so the source and the published artifact always match.

## Releasing
---
Releases are created with [semantic-release](https://semantic-release.gitbook.io/), the same setup that is used for the upstream project. The version of a release and its changelog are derived from the commit messages, which follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

| Commit | Release |
| --- | --- |
| `fix: ...` | patch, for example `1.0.1` |
| `feat: ...` | minor, for example `1.1.0` |
| `perf: ...` | patch |
| `build: Needs bump` | patch |
| `ci: ...`, `docs: ...`, `chore: ...` | no release |

The release workflow runs on a push to `main` and creates the stable release. To create a pre-release, run the `Release` workflow manually with the `dev` branch selected; the pre-releases are marked as such on GitHub and use the `~` notation Kodi expects, for example `1.0.0~dev.1`.

Every release attaches the built add-on zip, updates `CHANGELOG.md` and the `news` section of `addon.xml` and attests the provenance of the artifact.

## Continuous Integration
---
Builds and releases are automated with GitHub Actions (`.github/workflows`):

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `build_pull_request.yml` | push to `dev`, pull request to `dev` or `main` | Runs the test suite, validates the add-on, builds the zip and uploads it as a workflow artifact |
| `release.yml` | push to `main`, manual run | Runs the test suite and creates the release with semantic-release: changelog, version, tag, GitHub release with the add-on zip and the provenance attestation. A manual run on `dev` creates a pre-release |
| `open_pull_request.yml` | push to `dev` | Opens a draft pull request from `dev` to `main` |

The version line of this repository starts at `1.0.0`; the historic changelog of the upstream releases is kept in the `news` section of `addon.xml`.

The workflows that open pull requests (`open_pull_request.yml` and the back-merge job of `release.yml`) need the repository setting **Settings > Actions > General > Workflow permissions > Allow GitHub Actions to create and approve pull requests**. Without it the `GITHUB_TOKEN` is not allowed to create pull requests and the workflow reports a warning instead of failing.



