# Changelog

## 1.3.0

- Default flavor set is now `dev`, `stg`, `prod` (suffixes `.dev`, `.stg`, none). Projects without a config file get three flavors from `flavors`; `firebase --mode per-flavor` needs a `--flavor stg=...` mapping. Existing `android-app-config.json` files keep their own flavors.
- Replaced project-specific defaults (`Career Ops`, `CAREER_OPS_*`) with neutral ones (`My App`, `APP_ENVIRONMENT`, `APP_BASE_URL`).
- One flavor naming rule everywhere: `prod` keeps the app name; other flavors get `[DEV]`, `[STG]`, `[<FLAVOR>]` prefixes.
- `package-name` no longer creates `android-app-config.json`; it updates the file only when it already exists. Run `init` first to keep a config file.
- `package-name --app-name` renames every declared flavor and no longer creates resources for undeclared flavors.
- Added `.claude-plugin/marketplace.json` so Claude Code can install the plugin with `claude plugin marketplace add dthuy62/mobile-app-config`.
- Explicit `buildConfigFields` in a config file are no longer merged with the default `APP_ENVIRONMENT`/`APP_BASE_URL` fields; `init` on a project that already declares flavors keeps only its own fields.
- `package-name` now also renames Room schema export directories (`<module>/schemas/<old.package>.*`) to the new package, and fails before any write if a target directory already exists.

## 1.2.1

- Fixed Figma Variables CLI exports for split typography, decimal spacing names, and root-level radius number tokens.
- Kept spacing and radius number exports strictly filtered by token name or Figma scope.

## 1.2.0

- Added JSON CLI exports for spacing, radius, shadow, and typography design tokens.
- Kept existing color export behavior unchanged.
- Updated Flutter ThemeExtension output coverage for non-color token groups.

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
