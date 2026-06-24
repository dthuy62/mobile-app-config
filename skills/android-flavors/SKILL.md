---
name: android-flavors
description: Configure or validate Android product flavors with mobile-app-config. Use when the user says "/android-flavors", "/mobile-app-config flavors", "android mobile config flavors", "configure Android dev prod flavors", or asks to add Android productFlavors, applicationIdSuffix values, BuildConfig fields, or flavor-specific app names.
---

# Mobile App Config Flavors

Configure Android product flavors from the project root. Missing config is inferred in memory.

Run the canonical skill CLI from the Android project root:

```bash
~/.codex/skills/android/scripts/mobile-app-config flavors
```

Then validate:

```bash
~/.codex/skills/android/scripts/mobile-app-config validate-flavors
```

Run Gradle Sync in Android Studio after generation. Expected variants are `devDebug`, `prodDebug`, `devRelease`, and `prodRelease`.

Prefer the script over manual Gradle edits. Re-run once after changes to confirm idempotency when requested.
