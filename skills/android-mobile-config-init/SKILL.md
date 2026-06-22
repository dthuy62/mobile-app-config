---
name: android-mobile-config-init
description: Initialize android-mobile-config.json for an Android project. Use when the user says "/android-mobile-config-init", "/android-mobile-config init", "android mobile config init", or asks to create or refresh the Android mobile config file before configuring flavors, assets, or network security.
---

# Android Mobile Config Init

Initialize the config file from the Android project root.

Run the canonical skill CLI from the Android project root:

```bash
~/.codex/skills/android-mobile-config/scripts/android-mobile-config init
```

Use `--force` only when the user explicitly wants to replace an existing `android-mobile-config.json`.
