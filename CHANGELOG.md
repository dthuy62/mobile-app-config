# Changelog

## 0.3.0

- Added `package-name` and `validate-package-name` commands for syncing `applicationId`, namespace, and source packages.
- Added typed asset generation with `assets --type app-icons`, `assets --type splash-screens`, and `assets --type all`.
- Added modern Android app icon output: legacy launcher PNGs, adaptive icons, and optional monochrome themed icons.
- Added XML-only splash screen resources for Android 12+ and older Android, including optional night resources.

## 0.2.0

- Added Firebase CLI setup for single-project and per-flavor Android configs.
- Added `$android-mobile-config-firebase`, `firebase`, and `validate-firebase`.
- Added Google Services Gradle plugin wiring and Firebase validation.

## 0.1.0

- Initial standalone skill project.
- Added command-style skill entries for init, flavors, assets, network security, and help.
- Added deterministic Python CLI, validation scripts, Android fixtures, and packaging.
