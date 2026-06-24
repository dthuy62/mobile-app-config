# Mobile App Config

Mobile App Config is a Codex plugin for configuring mobile app environments from agent workflows. It gives Codex deterministic commands for Android product flavors, package names, Firebase multi-flavor config, flavor-specific app names, Android app assets, and optional network-security XML.

The plugin is designed for Codex Marketplace distribution first. Claude Code and standalone skill installs are supported as manual compatibility paths.

## Features

- Configure Kotlin Gradle Android product flavors idempotently.
- Create and validate `dev` and `prod` variants.
- Generate flavor-specific `app_name` resources.
- Add `applicationIdSuffix` and `BuildConfig` fields from config or inferred defaults.
- Sync Android `applicationId`, namespace, and Kotlin/Java source package declarations.
- Configure Firebase `google-services.json` for one shared Firebase project or one project per flavor.
- Create missing Firebase Android apps only when explicitly requested.
- Create `android-app-config.json` only when initializing or persisting explicit options.
- Generate legacy launcher icons, adaptive icons, optional themed icons, and XML-only splash screens.
- Configure Android network-security XML only when explicitly enabled.
- Refuse broad production cleartext traffic unless explicitly allowed.
- Expose focused command-style skills:
  - `$android`
  - `$android-init`
  - `$android-flavors`
  - `$android-firebase`
  - `$android-assets`
  - `$android-network-security`
  - `$android-help`

## Prerequisites

- Codex for marketplace or plugin usage.
- Python 3.9 or newer.
- An Android project with a Kotlin Gradle app module, usually `app/build.gradle.kts`.
- Optional: Firebase CLI for Firebase setup.
- Optional: Pillow 10 or newer for asset generation.

Install optional local CLI dependencies when developing this plugin:

```bash
python3 -m pip install -e ".[dev]"
```

Install asset-generation support:

```bash
python3 -m pip install -e ".[dev,assets]"
```

## Installation

### Codex Plugin Marketplace (Recommended)

This is the primary supported installation path.

Add the marketplace source:

```bash
codex plugin marketplace add dthuy62/mobile-app-config
```

Restart Codex and install `Mobile App Config` from the Codex plugin directory.

This repository includes the plugin metadata Codex expects:

```text
.agents/plugins/marketplace.json
.codex-plugin/plugin.json
skills/
```

For local marketplace testing:

```bash
git clone https://github.com/dthuy62/mobile-app-config.git mobile-app-config
codex plugin marketplace add ./mobile-app-config
```

Restart Codex after changing plugin metadata or skills.

### Claude Code Plugin Manual

Claude Code is supported manually through the plugin directory.

```bash
git clone https://github.com/dthuy62/mobile-app-config.git mobile-app-config
claude --plugin-dir ./mobile-app-config
```

Claude Code plugin metadata lives at:

```text
.claude-plugin/plugin.json
```

### Project-Specific Claude Plugin

Use this path when a single Android repository should carry the plugin with it.

```bash
mkdir -p tools
cp -R /path/to/mobile-app-config tools/mobile-app-config
claude --plugin-dir ./tools/mobile-app-config
```

Project-specific installs are useful for teams that want Android setup automation checked into the app repository.

## Usage

From Codex, invoke one of the skills:

```text
Use $android-flavors to configure dev and prod flavors.
Use $android to change Android package/applicationId.
Use $android-firebase to configure Firebase for Android flavors.
Use $android-assets to generate app icons and splash screens.
Use $android-network-security to enable local HTTP for dev only.
Use $android-help to show available commands.
```

From a shell in an Android project root:

```bash
mobile-app-config init
mobile-app-config flavors
mobile-app-config validate-flavors
mobile-app-config package-name --application-id com.aistudio.taskarena.kymzap
mobile-app-config package-name --application-id com.aistudio.taskarena.kymzap --app-name "Task Arena" --root-project-name "Task Arena"
mobile-app-config validate-package-name
mobile-app-config firebase
mobile-app-config validate-firebase
mobile-app-config assets --type app-icons --image branding/logo.png
mobile-app-config assets --type splash-screens --image branding/splash.png
mobile-app-config validate-assets --type all
mobile-app-config network-security
mobile-app-config validate-network-security
```

After running `mobile-app-config flavors`, run Gradle Sync in Android Studio. The expected variants are `devDebug`, `prodDebug`, `devRelease`, and `prodRelease`.

### Package name sync

Change the base Android package/application ID and sync source packages:

```bash
mobile-app-config package-name --application-id com.aistudio.taskarena.kymzap
mobile-app-config validate-package-name
```

The command updates app `namespace`, `defaultConfig.applicationId`, Kotlin/Java package folders, package declarations, and imports that reference the old package prefix. Optional `--app-name` updates display-name resources for `main`, `dev`, and `prod`; optional `--root-project-name` updates `settings.gradle.kts`. Flavor `applicationIdSuffix` values are preserved.

### Android app icons and splash screens

Generate modern Android app icons:

```bash
mobile-app-config assets --type app-icons --image branding/logo.png
```

Generate XML-only splash resources:

```bash
mobile-app-config assets --type splash-screens --image branding/splash.png
```

Generate both from one image:

```bash
mobile-app-config assets --type all --image branding/logo.png
```

Optional flags:

```bash
mobile-app-config assets --type app-icons \
  --image branding/logo.png \
  --background-color '#FFFFFF' \
  --monochrome-image branding/logo-mono.png

mobile-app-config assets --type splash-screens \
  --image branding/splash.png \
  --background-color '#FFFFFF' \
  --dark-image branding/splash-dark.png \
  --dark-background-color '#000000'
```

App icons include legacy `mipmap-*` PNGs, adaptive icon XML/resources for Android 8+, and optional monochrome themed icons for Android 13+ launchers. Generated PNG launcher resources replace stale same-name WebP/XML launcher resources.

Splash screens use Android 12+ platform splash attrs plus legacy `windowBackground` resources for Android 11 and below. Android 12+ splash screens are icon plus background, not full-screen artwork. The plugin does not add AndroidX SplashScreen or call `installSplashScreen()`.

### Firebase multi-flavor setup

Install Firebase CLI and log in locally:

```bash
npm install -g firebase-tools
firebase login
```

Use one Firebase project for every flavor:

```bash
mobile-app-config firebase --mode single --project my-firebase
```

Use one Firebase project per flavor:

```bash
mobile-app-config firebase --mode per-flavor --flavor dev=my-dev --flavor prod=my-prod
```

Create missing Firebase Android apps only when explicitly requested:

```bash
mobile-app-config firebase --mode single --project my-firebase --create-apps
```

Validate generated files:

```bash
mobile-app-config validate-firebase
```

If Firebase CLI is not logged in, the command stops. Run `firebase login`, then rerun the same `mobile-app-config firebase` command.

If the Python package is not installed, call the bundled CLI directly:

```bash
python3 /path/to/mobile-app-config/skills/android/scripts/mobile-app-config flavors
```

Default behavior:

- Missing `android-app-config.json` is inferred in memory.
- `init` creates `android-app-config.json`; commands with explicit persisted options update it.
- `firebase` exits as a clear no-op unless `firebase.enabled=true` or Firebase flags are provided.
- Firebase auth uses local Firebase CLI login. If needed, run `firebase login`, then rerun the command.
- `assets` exits as a clear no-op unless `assets.enabled=true` or asset flags are provided.
- `network-security` exits as a clear no-op unless `networkSecurity.enabled=true`.

## Structure

```text
mobile-app-config/
  .agents/plugins/marketplace.json      Codex marketplace catalog
  .codex-plugin/plugin.json             Codex plugin manifest
  .claude-plugin/plugin.json            Claude Code plugin manifest
  skills/
    android/              Canonical Android skill with CLI and references
    android-init/         Command-style skill
    android-flavors/      Command-style skill
    android-firebase/     Command-style skill
    android-assets/       Command-style skill
    android-network-security/
    android-help/
  scripts/
    validate_skill.py                   Skill and metadata validator
  tests/                                Pytest suite and Android fixtures
```

## Development

```bash
python3 -m pip install -e ".[dev]"
python3 scripts/validate_skill.py
python3 -m pytest
```

The test suite uses small Kotlin Gradle Android fixtures and does not require building a real Android app.

## References

- Codex plugin build guide: [https://developers.openai.com/codex/plugins/build](https://developers.openai.com/codex/plugins/build)
- Claude Code plugin guide: [https://code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins)

## License

MIT
