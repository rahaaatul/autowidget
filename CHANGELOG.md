## [1.1.0-dev.4](https://github.com/rahaaatul/autowidget/compare/v1.1.0-dev.3...v1.1.0-dev.4) (2026-10-23)

### ✨ New Features

* **settings:** rename widgets.merged_sort to widgets.sort with 9 sort options at basic level ([327012f](https://github.com/rahaaatul/autowidget/commit/327012fc307068941320942a377094feb6a69883))
* **settings:** split the settings into the four levels of Kodi ([6165f06](https://github.com/rahaaatul/autowidget/commit/6165f06c620e58320682f72ab8bb73ad30f5e64b))

## [1.1.0-dev.3](https://github.com/rahaaatul/autowidget/compare/v1.1.0-dev.2...v1.1.0-dev.3) (2026-10-22)

### 🐛 Bug Fixes

* **cache:** keep the changes of a path instead of a sample on every update ([d1b5195](https://github.com/rahaaatul/autowidget/commit/d1b51950fac857a1a3386c8d19ccb9377d3ea764))

## [1.1.0-dev.2](https://github.com/rahaaatul/autowidget/compare/v1.1.0-dev.1...v1.1.0-dev.2) (2026-10-21)

### ✨ New Features

* **menu:** sort the merged widget from its context menu ([d584bb2](https://github.com/rahaaatul/autowidget/commit/d584bb22f8b3aa14e5eebb2266e9aa67af924156))

### 🚀 Continuous Integration

* back-merge main into dev after a release ([a4295d6](https://github.com/rahaaatul/autowidget/commit/a4295d677ba4a979dd7bea0f257d4fed51685a4a))

## [1.1.0-dev.1](https://github.com/rahaaatul/autowidget/compare/v1.0.0...v1.1.0-dev.1) (2026-10-21)

### ✨ New Features

* **menu:** sort the items of a merged widget ([809c476](https://github.com/rahaaatul/autowidget/commit/809c47622b6ac35fe6ab634527c2bf86953ec3ca))

## 1.0.0 (2026-10-21)

### ⚠ BREAKING CHANGES

* target Kodi 21.3 (Omega) only and drop the six dependency

### ✨ New Features

* reimplement the outstanding upstream pull requests ([27a01f0](https://github.com/rahaaatul/autowidget/commit/27a01f0f4a3b28dd4c881a600172de28ca3e014b)), closes [#39](https://github.com/rahaaatul/autowidget/issues/39) [#61](https://github.com/rahaaatul/autowidget/issues/61) [#76](https://github.com/rahaaatul/autowidget/issues/76)
* **ui:** add support for Kodi 21 (Omega) ([e30f3fa](https://github.com/rahaaatul/autowidget/commit/e30f3fafa557339bf24203458ce7dc90cdc34887))
* **widget:** add a widget mode for skin widgets ([e9f5cd1](https://github.com/rahaaatul/autowidget/commit/e9f5cd1f8fb7645360b02c6fb470ba46ae5a1f21))

### 🐛 Bug Fixes

* **artwork:** publish local artwork as an absolute path ([b89fdfd](https://github.com/rahaaatul/autowidget/commit/b89fdfdd3eb52a7220fecf75b9775e69e2d740fe))
* **cache:** keep the service alive when a path can not be updated ([e4a74e4](https://github.com/rahaaatul/autowidget/commit/e4a74e48d146abe7439d353413f4985ca7948cf7))
* **ci:** keep the python cache out of the repository ([92c4cb0](https://github.com/rahaaatul/autowidget/commit/92c4cb0695112ea7d3fd6513f389426f3b63fb64))
* **ci:** keep the release version in the name of the add-on zip ([7dfdc5e](https://github.com/rahaaatul/autowidget/commit/7dfdc5e0d6de5bb27c79c9d95eb302232d84dc43))
* **edit:** change the paths of the merged widget the skin uses ([594f0b6](https://github.com/rahaaatul/autowidget/commit/594f0b658d509e05f7695209e8adec5f29796dbd))
* **edit:** resolve the widget paths by their id ([1a4f5ee](https://github.com/rahaaatul/autowidget/commit/1a4f5ee69b6bad1e722af353aa3437efbb69931e))
* **i18n:** apply the remaining French corrections of upstream PR [#154](https://github.com/rahaaatul/autowidget/issues/154) ([2749033](https://github.com/rahaaatul/autowidget/commit/2749033fc055f24a20e6880c26e28e21dacf873d))
* **menu:** drop the action separator from the group listing ([20c64e6](https://github.com/rahaaatul/autowidget/commit/20c64e6e774dc0ff7a197799dd7753b28cccd1de))
* **menu:** merge all the paths of a group without asking ([c3c5096](https://github.com/rahaaatul/autowidget/commit/c3c5096a2a2c1e9a3fc446515a977ffec2a0442b))
* **menu:** move the paths action to the merged entry of the group ([fbcabab](https://github.com/rahaaatul/autowidget/commit/fbcababaafd53049bf0fee6d111e4cbb86f0f59c))
* **menu:** open the merged widget of the group in the merged entry ([ad4fb34](https://github.com/rahaaatul/autowidget/commit/ad4fb3407e96a798d4fc9a936426e1cbd33376a0))
* **player:** keep the playback type defined when a playback ends ([41c011e](https://github.com/rahaaatul/autowidget/commit/41c011e77e417bb404614891393da5368b165a6e))
* **refresh:** refresh the widgets during playback when enabled ([caaefbc](https://github.com/rahaaatul/autowidget/commit/caaefbcfaa35199b378f932369680ed01f8867a3))
* **refresh:** reload the AutoWidget container in a media window ([7f03a2e](https://github.com/rahaaatul/autowidget/commit/7f03a2ebcf98ad19ac57d98d7d88bfb439303067))
* **utils:** reload the container while a library scan is running ([20444f2](https://github.com/rahaaatul/autowidget/commit/20444f2108f6684d64ba31e44ca8fd8261b657c6))

### ♻️ Refactoring

* target Kodi 21.3 (Omega) only and drop the six dependency ([59bc96d](https://github.com/rahaaatul/autowidget/commit/59bc96db1124d15705e12af712a4b4cb6a6abc7d))

### 🚀 Continuous Integration

* follow the Kodi repository layout and reset the add-on version to 1.0.0 ([c535b90](https://github.com/rahaaatul/autowidget/commit/c535b90475fe4ebc238fca33492ba6ae77e50fce))
* **Needs bump:** release with semantic-release ([b26aa24](https://github.com/rahaaatul/autowidget/commit/b26aa24d944ce27da8d816708a3dad7826855f2b))
* replace CircleCI with GitHub Actions build and release workflows ([4ca3caa](https://github.com/rahaaatul/autowidget/commit/4ca3caa7307d7f2eedc14c2f8b866eb507e42df9))
* run the test suite in the GitHub Actions workflows ([6e842a5](https://github.com/rahaaatul/autowidget/commit/6e842a5eea0751a5c4388a5c4afc2fddd0959108))
* skip pull requests without differences and tolerate a disabled PR permission ([73e0202](https://github.com/rahaaatul/autowidget/commit/73e02026dd3a06977765709ba7605e17c81c4d7c))

## [1.0.0-dev.8](https://github.com/rahaaatul/autowidget/compare/v1.0.0-dev.7...v1.0.0-dev.8) (2026-10-21)

### 🐛 Bug Fixes

* **menu:** open the merged widget of the group in the merged entry ([ad4fb34](https://github.com/rahaaatul/autowidget/commit/ad4fb3407e96a798d4fc9a936426e1cbd33376a0))

## [1.0.0-dev.7](https://github.com/rahaaatul/autowidget/compare/v1.0.0-dev.6...v1.0.0-dev.7) (2026-10-21)

### 🐛 Bug Fixes

* **edit:** change the paths of the merged widget the skin uses ([594f0b6](https://github.com/rahaaatul/autowidget/commit/594f0b658d509e05f7695209e8adec5f29796dbd))

## [1.0.0-dev.6](https://github.com/rahaaatul/autowidget/compare/v1.0.0-dev.5...v1.0.0-dev.6) (2026-10-21)

### 🐛 Bug Fixes

* **menu:** move the paths action to the merged entry of the group ([fbcabab](https://github.com/rahaaatul/autowidget/commit/fbcababaafd53049bf0fee6d111e4cbb86f0f59c))

## [1.0.0-dev.5](https://github.com/rahaaatul/autowidget/compare/v1.0.0-dev.4...v1.0.0-dev.5) (2026-10-21)

### 🐛 Bug Fixes

* **menu:** merge all the paths of a group without asking ([c3c5096](https://github.com/rahaaatul/autowidget/commit/c3c5096a2a2c1e9a3fc446515a977ffec2a0442b))

## [1.0.0-dev.4](https://github.com/rahaaatul/autowidget/compare/v1.0.0-dev.3...v1.0.0-dev.4) (2026-10-21)

### 🐛 Bug Fixes

* **edit:** resolve the widget paths by their id ([1a4f5ee](https://github.com/rahaaatul/autowidget/commit/1a4f5ee69b6bad1e722af353aa3437efbb69931e))
* **menu:** drop the action separator from the group listing ([20c64e6](https://github.com/rahaaatul/autowidget/commit/20c64e6e774dc0ff7a197799dd7753b28cccd1de))

## [1.0.0-dev.3](https://github.com/rahaaatul/autowidget/compare/v1.0.0-dev.2...v1.0.0-dev.3) (2026-10-21)

### 🐛 Bug Fixes

* **artwork:** publish local artwork as an absolute path ([b89fdfd](https://github.com/rahaaatul/autowidget/commit/b89fdfdd3eb52a7220fecf75b9775e69e2d740fe))
* **player:** keep the playback type defined when a playback ends ([41c011e](https://github.com/rahaaatul/autowidget/commit/41c011e77e417bb404614891393da5368b165a6e))
* **refresh:** refresh the widgets during playback when enabled ([caaefbc](https://github.com/rahaaatul/autowidget/commit/caaefbcfaa35199b378f932369680ed01f8867a3))
* **refresh:** reload the AutoWidget container in a media window ([7f03a2e](https://github.com/rahaaatul/autowidget/commit/7f03a2ebcf98ad19ac57d98d7d88bfb439303067))

## [1.0.0-dev.2](https://github.com/rahaaatul/autowidget/compare/v1.0.0-dev.1...v1.0.0-dev.2) (2026-10-21)

### ✨ New Features

* **widget:** add a widget mode for skin widgets ([e9f5cd1](https://github.com/rahaaatul/autowidget/commit/e9f5cd1f8fb7645360b02c6fb470ba46ae5a1f21))

### 🐛 Bug Fixes

* **cache:** keep the service alive when a path can not be updated ([e4a74e4](https://github.com/rahaaatul/autowidget/commit/e4a74e48d146abe7439d353413f4985ca7948cf7))

## 1.0.0-dev.1 (2026-10-21)

### ⚠ BREAKING CHANGES

* target Kodi 21.3 (Omega) only and drop the six dependency

### ✨ New Features

* reimplement the outstanding upstream pull requests ([27a01f0](https://github.com/rahaaatul/autowidget/commit/27a01f0f4a3b28dd4c881a600172de28ca3e014b)), closes [#39](https://github.com/rahaaatul/autowidget/issues/39) [#61](https://github.com/rahaaatul/autowidget/issues/61) [#76](https://github.com/rahaaatul/autowidget/issues/76)
* **ui:** add support for Kodi 21 (Omega) ([e30f3fa](https://github.com/rahaaatul/autowidget/commit/e30f3fafa557339bf24203458ce7dc90cdc34887))

### 🐛 Bug Fixes

* **ci:** keep the python cache out of the repository ([92c4cb0](https://github.com/rahaaatul/autowidget/commit/92c4cb0695112ea7d3fd6513f389426f3b63fb64))
* **ci:** keep the release version in the name of the add-on zip ([7dfdc5e](https://github.com/rahaaatul/autowidget/commit/7dfdc5e0d6de5bb27c79c9d95eb302232d84dc43))
* **i18n:** apply the remaining French corrections of upstream PR [#154](https://github.com/rahaaatul/autowidget/issues/154) ([2749033](https://github.com/rahaaatul/autowidget/commit/2749033fc055f24a20e6880c26e28e21dacf873d))

### ♻️ Refactoring

* target Kodi 21.3 (Omega) only and drop the six dependency ([59bc96d](https://github.com/rahaaatul/autowidget/commit/59bc96db1124d15705e12af712a4b4cb6a6abc7d))

### 🚀 Continuous Integration

* follow the Kodi repository layout and reset the add-on version to 1.0.0 ([c535b90](https://github.com/rahaaatul/autowidget/commit/c535b90475fe4ebc238fca33492ba6ae77e50fce))
* **Needs bump:** release with semantic-release ([b26aa24](https://github.com/rahaaatul/autowidget/commit/b26aa24d944ce27da8d816708a3dad7826855f2b))
* replace CircleCI with GitHub Actions build and release workflows ([4ca3caa](https://github.com/rahaaatul/autowidget/commit/4ca3caa7307d7f2eedc14c2f8b866eb507e42df9))
* run the test suite in the GitHub Actions workflows ([6e842a5](https://github.com/rahaaatul/autowidget/commit/6e842a5eea0751a5c4388a5c4afc2fddd0959108))
* skip pull requests without differences and tolerate a disabled PR permission ([73e0202](https://github.com/rahaaatul/autowidget/commit/73e02026dd3a06977765709ba7605e17c81c4d7c))

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Conventional Commits](https://www.conventionalcommits.org/)
and the releases are created with [semantic-release](https://semantic-release.gitbook.io/).

## [1.0.0](https://github.com/rahaaatul/autowidget/releases/tag/v1.0.0) (2026-10-21)

### ✨ New Features

* reset the add-on version to 1.0.0 and start a new release line
* reimplement the outstanding upstream pull requests
* add support for Kodi 21 (Omega)
* build and release the add-on with GitHub Actions and semantic-release

### 🐛 Bug Fixes

* target Kodi 21 "Omega" (21.3 or later) and drop support for older releases
* use the Pillow version provided by Kodi
* fix direct shortcuts and settings shortcuts for dependency add-ons
