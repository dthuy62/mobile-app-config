---
name: android-init
description: Initialize android-app-config.json for an Android project. Use when the user says "/android-init", "/mobile-app-config init", "android mobile config init", or asks to create or refresh the Android mobile config file before configuring flavors, assets, or network security.
---

# Mobile App Config Init

Initialize the config file from the Android project root.

Resolve `../android/scripts/mobile-app-config` relative to this `SKILL.md`, then run it from the Android project root:

```bash
<resolved-script> init
```

Use `--force` only when the user explicitly wants to replace an existing `android-app-config.json`.
