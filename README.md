# AutoWidget

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/840a4c0ed72e4d25b3d82c984e3c4b84)](https://app.codacy.com/manual/drinfernoo/plugin.program.autowidget?utm_source=github.com&utm_medium=referral&utm_content=drinfernoo/plugin.program.autowidget&utm_campaign=Badge_Grade_Dashboard)
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
1.  Go to the Kodi file manager.
2.  Click on "Add source".
3.  The path for the source is `https://github.com/rahaaatul/autowidget/raw/repo/` (Give it the name "rahaaatul").
4.  Go to "Add-ons", and choose "Install from zip file".
5.  Install `repository.autowidget-1.1.zip` from the source you just added.
6.  Return to "Add-ons", and choose "Install from repository".
7.  Choose the "AutoWidget Repository" you installed, and install AutoWidget from Program Add-ons.


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

# Build the installable add-on zip (the version is stamped into addon.xml)
python3 .github/scripts/build_addon.py --version 1.0.0 --addon-path plugin.program.autowidget --output-dir dist

# Build the repository add-on zip
python3 .github/scripts/build_addon.py --version 1.1 --addon-path repository.autowidget --output-dir dist

# Generate the Kodi repository (addons.xml, checksums, add-on folder)
python3 .github/scripts/generate_repository.py --version 1.0.0 \
    --addon-zip dist/plugin.program.autowidget-1.0.0.zip --output-dir dist/repository
```

The version in `plugin.program.autowidget/addon.xml` is the version of the current release (`1.0.0`). The release workflow replaces it with the released version while packaging, so a released artifact always matches its tag.

The add-on follows the [Kodi add-on and repository layout](https://kodi.wiki/view/Add-on_repositories):

```
zips/
  addons.xml                  index of the add-ons in the repository
  addons.xml.md5              checksum of addons.xml
  plugin.program.autowidget/
    plugin.program.autowidget-1.0.0.zip
    plugin.program.autowidget-1.0.0.zip.md5
    icon.png, fanart.png, ... assets of the add-on
    changelog-1.0.0.txt
repository.autowidget-1.1.zip  the repository add-on, installed by the user
```

## Continuous Integration
---
Builds and releases are automated with GitHub Actions (`.github/workflows`):

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `build_pull_request.yml` | push to `dev`, pull request to `dev` or `main` | Runs the test suite, validates the add-on, builds the zip and uploads it as a workflow artifact |
| `release.yml` | tag `v*` push, manual run | Builds the add-on and the repository add-on, creates a GitHub release with the zips attached, attests the provenance, back-merges `main` into `dev` and publishes the Kodi repository to the `repo` branch |
| `open_pull_request.yml` | push to `dev` | Opens a draft pull request from `dev` to `main` |

Releasing is done by pushing a tag, for example `git tag v1.0.0 && git push origin v1.0.0`. The workflow publishes the add-on zip, the repository add-on zip and the generated Kodi repository to the `repo` branch, which is the location the `repository.autowidget` add-on points at.

The version line of this repository starts at `1.0.0`; the historic changelog of the upstream releases is kept in the `news` section of `addon.xml`.

The workflows that open pull requests (`open_pull_request.yml` and the back-merge job of `release.yml`) need the repository setting **Settings > Actions > General > Workflow permissions > Allow GitHub Actions to create and approve pull requests**. Without it the `GITHUB_TOKEN` is not allowed to create pull requests and the workflow reports a warning instead of failing.



