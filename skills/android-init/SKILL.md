---
name: android-init
description: Initialize android-app-config.json for an Android project. Use when the user says "/android-init", "/mobile-app-config init", "android mobile config init", or asks to create or refresh the Android mobile config file before configuring flavors, assets, or network security.
---

# Mobile App Config Init

Initialize the config file from the Android project root.

Use the bundled CLI at `../android/scripts/mobile-app-config`, resolved relative to this `SKILL.md`. Run it with cwd set to the Android project root.

```bash
mobile-app-config init
```

Use `--force` only when the user explicitly wants to replace an existing `android-app-config.json`.
