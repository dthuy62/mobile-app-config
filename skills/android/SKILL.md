---
name: android
description: Configure Android mobile app project setup with deterministic scripts for product flavors, flavor-specific app names, package names, Firebase multi-flavor config, launcher/adaptive/splash assets, and optional Android network security config. Use when the user asks to add or validate dev/prod Android flavors, change Android package/applicationId, Firebase google-services.json setup, generate Android app icons or splash screens, create android-app-config.json, or configure Android network-security XML for local/dev builds.
---

# Mobile App Config

Use this skill for Android app configuration tasks that are fragile to edit by hand. Prefer the bundled CLI scripts over manual Gradle, manifest, or resource edits.

## Quick Start

Use the bundled CLI at `scripts/mobile-app-config`, resolved relative to this `SKILL.md`. Run it with cwd set to the Android project root.

```bash
mobile-app-config flavors
mobile-app-config package-name --application-id com.example.app
mobile-app-config firebase --mode single --project my-firebase
mobile-app-config assets --type all --image branding/logo.png
mobile-app-config network-security
```

Commands infer Android defaults in memory when `android-app-config.json` is missing. `init` creates the file, and commands that persist explicit options update it.

## Workflow

1. Inspect the current project root and confirm the Android app module.
2. Run the relevant script instead of hand-editing generated sections.
3. Run the matching validation command or Android Gradle task.
4. Re-run the command when checking idempotency; the second run should not duplicate Gradle blocks, resource files, or manifest attributes.
5. After flavor generation, run Gradle Sync in Android Studio; expected variants are `devDebug`, `prodDebug`, `devRelease`, and `prodRelease`.

## Commands

- `mobile-app-config init`: create `android-app-config.json`; pass `--force` only when intentionally replacing an existing config.
- `mobile-app-config flavors`: configure product flavors and flavor-specific `app_name` resources.
- `mobile-app-config validate-flavors`: validate configured flavors and expected task names.
- `mobile-app-config package-name`: sync `applicationId`, namespace, Kotlin/Java source package declarations, optional `--app-name`, and optional `--root-project-name`.
- `mobile-app-config validate-package-name`: validate package-name sync.
- `mobile-app-config firebase`: configure Firebase `google-services.json` files using Firebase CLI when `firebase.enabled=true` or Firebase flags are provided.
- `mobile-app-config validate-firebase`: validate Firebase config files, package names, and Google Services Gradle plugin wiring.
- `mobile-app-config assets`: generate app icons or splash screens by type.
- `mobile-app-config validate-assets`: validate generated asset resources by type.
- `mobile-app-config network-security`: configure network security only when `networkSecurity.enabled=true`.
- `mobile-app-config validate-network-security`: validate network-security files and manifest references.

Splash resources use Android 12+ platform attrs and Android 11-and-below `windowBackground`. This plugin does not add AndroidX SplashScreen or call `installSplashScreen()`.

## References

- Read `references/config-schema.md` before changing config shape.
- Read `references/android-flavors.md` before changing Gradle flavor behavior.
- Read `references/firebase.md` before changing Firebase behavior.
- Read `references/android-assets.md` before changing asset generation.
- Read `references/network-security.md` before changing network-security behavior.
