# Mobile App Config

Mobile App Config is a Codex plugin for configuring mobile app environments from agent workflows. It gives Codex deterministic commands for Android product flavors, package names, Firebase multi-flavor config, flavor-specific app names, Android app assets, and optional network-security XML.

The plugin is designed for Codex Marketplace distribution first. Claude Code and standalone skill installs are supported as manual compatibility paths.

## Features

- Configure Kotlin Gradle Android product flavors idempotently.
- Create and validate `dev` and `prod` variants.
- Generate flavor-specific `app_name` resources.
- Add `applicationIdSuffix` and `BuildConfig` fields from `android-mobile-config.json`.
- Sync Android `applicationId`, namespace, and Kotlin/Java source package declarations.
- Configure Firebase `google-services.json` for one shared Firebase project or one project per flavor.
- Create missing Firebase Android apps only when explicitly requested.
- Auto-create `android-mobile-config.json` from the current Android project when it is missing.
- Generate legacy launcher icons, adaptive icons, optional themed icons, and XML-only splash screens.
- Configure Android network-security XML only when explicitly enabled.
- Refuse broad production cleartext traffic unless explicitly allowed.
- Expose focused command-style skills:
  - `$android-mobile-config`
  - `$android-mobile-config-init`
  - `$android-mobile-config-flavors`
  - `$android-mobile-config-firebase`
  - `$android-mobile-config-assets`
  - `$android-mobile-config-network-security`
  - `$android-mobile-config-help`

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

### Codex Plugin Marketplace

This is the primary installation path.

After the plugin is published, add the marketplace source:

```bash
codex plugin marketplace add dthuy62/mobile-app-config
```

Then restart Codex and install `Mobile App Config` from the Codex plugin directory.

This repository includes the marketplace and plugin metadata Codex expects:

```text
.agents/plugins/marketplace.json
.codex-plugin/plugin.json
skills/
```

For local marketplace testing before publication:

```bash
git clone https://github.com/dthuy62/mobile-app-config.git mobile-app-config
codex plugin marketplace add ./mobile-app-config
```

Restart Codex after changing plugin metadata or skills.

### Codex Plugin Manual

Use this path while developing the plugin locally.

```bash
git clone https://github.com/dthuy62/mobile-app-config.git mobile-app-config
cd mobile-app-config
python3 scripts/validate_skill.py
python3 scripts/build_dist.py
codex plugin marketplace add .
```

Codex loads plugins through a marketplace entry, even for local plugin testing. The local marketplace catalog in this repo points to the plugin root.

### Claude Code Plugin Manual

Claude Code is supported manually. Marketplace packaging for Claude Code is not the primary target of this repo.

```bash
git clone https://github.com/dthuy62/mobile-app-config.git mobile-app-config
claude --plugin-dir ./mobile-app-config
```

Claude Code plugin metadata lives at:

```text
.claude-plugin/plugin.json
```

### Claude Code Skill Manual

If you only want the skills and not the plugin wrapper:

```bash
mkdir -p ~/.claude/skills
cp -R skills/android-mobile-config* ~/.claude/skills/
```

Restart Claude Code after copying.

### Codex Skill Manual

For local skill-only usage without Codex plugin installation:

```bash
git clone https://github.com/dthuy62/mobile-app-config.git mobile-app-config
cd mobile-app-config
python3 scripts/install_local_symlinks.py
```

This symlinks every skill folder into `~/.codex/skills`.

### Other AI Coding Tools

For tools such as Cursor, Antigravity, or other agent hosts, use the skill folders directly:

```text
skills/android-mobile-config/
skills/android-mobile-config-init/
skills/android-mobile-config-flavors/
skills/android-mobile-config-firebase/
skills/android-mobile-config-assets/
skills/android-mobile-config-network-security/
skills/android-mobile-config-help/
```

If the host does not support skills, point its project rules or agent instructions at `skills/android-mobile-config/SKILL.md` and run the bundled CLI from the Android project root.

### Project-Specific

Use this path when a single Android repository should carry the workflow with it.

Codex-style project install:

```bash
mkdir -p .codex/skills
cp -R /path/to/android-mobile-config/skills/android-mobile-config* .codex/skills/
```

Claude-style project install:

```bash
mkdir -p .claude/skills
cp -R /path/to/android-mobile-config/skills/android-mobile-config* .claude/skills/
```

Project-specific installs are useful for teams that want Android setup automation checked into the app repository.

## Usage

From Codex, invoke one of the skills:

```text
Use $android-mobile-config-flavors to configure dev and prod flavors.
Use $android-mobile-config to change Android package/applicationId.
Use $android-mobile-config-firebase to configure Firebase for Android flavors.
Use $android-mobile-config-assets to generate app icons and splash screens.
Use $android-mobile-config-network-security to enable local HTTP for dev only.
Use $android-mobile-config-help to show available commands.
```

From a shell in an Android project root:

```bash
mobile-app-config init
mobile-app-config flavors
mobile-app-config validate-flavors
mobile-app-config package-name --application-id com.aistudio.taskarena.kymzap
mobile-app-config validate-package-name
mobile-app-config firebase
mobile-app-config validate-firebase
mobile-app-config assets --type app-icons --image branding/logo.png
mobile-app-config assets --type splash-screens --image branding/splash.png
mobile-app-config validate-assets --type all
mobile-app-config network-security
mobile-app-config validate-network-security
```

`android-mobile-config` remains available as a backward-compatible CLI alias.

### Package name sync

Change the base Android package/application ID and sync source packages:

```bash
mobile-app-config package-name --application-id com.aistudio.taskarena.kymzap
mobile-app-config validate-package-name
```

The command updates app `namespace`, `defaultConfig.applicationId`, Kotlin/Java package folders, package declarations, and imports that reference the old package prefix. Flavor `applicationIdSuffix` values are preserved.

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

App icons include legacy `mipmap-*` PNGs, adaptive icon XML/resources for Android 8+, and optional monochrome themed icons for Android 13+ launchers. Splash screens use Android 12+ platform splash attrs plus legacy `windowBackground` resources for older Android. Android 12+ splash screens are icon plus background, not full-screen artwork.

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
python3 /path/to/mobile-app-config/skills/android-mobile-config/scripts/mobile-app-config flavors
```

Default behavior:

- Missing `android-mobile-config.json` is auto-created from the current project.
- Existing config is not rewritten unless `init --force` is used.
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
    android-mobile-config/              Canonical Android skill with CLI and references
    android-mobile-config-init/         Command-style skill
    android-mobile-config-flavors/      Command-style skill
    android-mobile-config-firebase/     Command-style skill
    android-mobile-config-assets/       Command-style skill
    android-mobile-config-network-security/
    android-mobile-config-help/
  scripts/
    install_local_symlinks.py           Local Codex skill installer
    validate_skill.py                   Skill and metadata validator
    build_dist.py                       Skill archive builder
  tests/                                Pytest suite and Android fixtures
  dist/                                 Generated release output
```

## Platform Output Directories


| Target                    | Install location or source                    | Notes                                          |
| ------------------------- | --------------------------------------------- | ---------------------------------------------- |
| Codex Marketplace         | `.agents/plugins/marketplace.json`            | Primary distribution path                      |
| Codex Plugin              | `.codex-plugin/plugin.json` and `skills/`     | Plugin root is this repository                 |
| Codex Skill Manual        | `~/.codex/skills/<skill-name>`                | Created by `scripts/install_local_symlinks.py` |
| Claude Code Plugin Manual | `claude --plugin-dir ./mobile-app-config`     | Uses `.claude-plugin/plugin.json`              |
| Claude Code Skill Manual  | `~/.claude/skills/<skill-name>`               | Copy `skills/android-mobile-config*`           |
| Project-specific Codex    | `<project>/.codex/skills/<skill-name>`        | Copy skill folders into the Android repo       |
| Project-specific Claude   | `<project>/.claude/skills/<skill-name>`       | Copy skill folders into the Android repo       |
| Other AI coding tools     | tool-specific rules or skill folders          | Use `skills/` and the bundled CLI              |


Build distributable skill folders:

```bash
python3 scripts/build_dist.py
```

Output:

```text
dist/mobile-app-config-skills/
dist/mobile-app-config-skills.zip
```

## Development

```bash
python3 -m pip install -e ".[dev]"
python3 scripts/validate_skill.py
python3 -m pytest
python3 scripts/build_dist.py
```

The test suite uses small Kotlin Gradle Android fixtures and does not require building a real Android app.

## References

- Codex plugin build guide: [https://developers.openai.com/codex/plugins/build](https://developers.openai.com/codex/plugins/build)
- Claude Code plugin guide: [https://code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins)

## License

MIT
