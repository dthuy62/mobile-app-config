---
name: android-mobile-config
description: Configure Android mobile app project setup with deterministic scripts for product flavors, flavor-specific app names, Firebase multi-flavor config, launcher/adaptive/splash/notification assets, and optional Android network security config. Use when the user asks to add or validate dev/prod Android flavors, Firebase google-services.json setup, generate Android app icons or splash assets, create android-mobile-config.json, or configure Android network-security XML for local/dev builds.
---

# Android Mobile Config

Use this skill for Android app configuration tasks that are fragile to edit by hand. Prefer the bundled CLI scripts over manual Gradle, manifest, or resource edits.

## Quick Start

Run commands from the Android project root:

```bash
~/.codex/skills/android-mobile-config/scripts/android-mobile-config flavors
~/.codex/skills/android-mobile-config/scripts/android-mobile-config firebase --mode single --project my-firebase
~/.codex/skills/android-mobile-config/scripts/android-mobile-config assets
~/.codex/skills/android-mobile-config/scripts/android-mobile-config network-security
```

If `android-mobile-config.json` is missing, each command auto-creates it from the current Android project and then continues. Existing config is never rewritten unless `init --force` is used.

## Workflow

1. Inspect the current project root and confirm the Android app module.
2. Run the relevant script instead of hand-editing generated sections.
3. Run the matching validation command or Android Gradle task.
4. Re-run the command when checking idempotency; the second run should not duplicate Gradle blocks, resource files, or manifest attributes.

## Commands

- `android-mobile-config init`: create `android-mobile-config.json`; pass `--force` only when intentionally replacing an existing config.
- `android-mobile-config flavors`: configure product flavors and flavor-specific `app_name` resources.
- `android-mobile-config validate-flavors`: validate configured flavors and expected task names.
- `android-mobile-config firebase`: configure Firebase `google-services.json` files using Firebase CLI when `firebase.enabled=true` or Firebase flags are provided.
- `android-mobile-config validate-firebase`: validate Firebase config files, package names, and Google Services Gradle plugin wiring.
- `android-mobile-config assets`: generate Android assets only when `assets.enabled=true`.
- `android-mobile-config validate-assets`: validate generated asset resources.
- `android-mobile-config network-security`: configure network security only when `networkSecurity.enabled=true`.
- `android-mobile-config validate-network-security`: validate network-security files and manifest references.

## References

- Read `references/config-schema.md` before changing config shape.
- Read `references/android-flavors.md` before changing Gradle flavor behavior.
- Read `references/firebase.md` before changing Firebase behavior.
- Read `references/android-assets.md` before changing asset generation.
- Read `references/network-security.md` before changing network-security behavior.
