---
name: android-mobile-config-flavors
description: Configure or validate Android product flavors with android-mobile-config. Use when the user says "/android-mobile-config-flavors", "/android-mobile-config flavors", "android mobile config flavors", "configure Android dev prod flavors", or asks to add Android productFlavors, applicationIdSuffix values, BuildConfig fields, or flavor-specific app names.
---

# Android Mobile Config Flavors

Configure Android product flavors from the project root. If `android-mobile-config.json` is missing, the script auto-creates it first.

Run the canonical skill CLI from the Android project root:

```bash
~/.codex/skills/android-mobile-config/scripts/android-mobile-config flavors
```

Then validate:

```bash
~/.codex/skills/android-mobile-config/scripts/android-mobile-config validate-flavors
```

Prefer the script over manual Gradle edits. Re-run once after changes to confirm idempotency when requested.
