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
