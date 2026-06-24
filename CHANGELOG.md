# Changelog

## 1.0.0

- Made Codex Marketplace the primary supported install path.
- Removed unsupported Codex skill symlink and dist archive flows.
- Updated skill instructions to resolve the bundled CLI relative to each `SKILL.md`.
- Added packaging contract tests to prevent local absolute paths and stale install docs.
- Added optional `package-name --app-name` and `--root-project-name` support.

## 0.5.0

- Fixed `package-name` to sync divergent Android identities by resolving source packages from Gradle namespace and Kotlin/Java declarations.
- Added fail-fast handling for ambiguous source package roots before source rewrites.
- Added regression coverage for divergent package sync, validation errors, idempotency, and partial-write preflight.

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
