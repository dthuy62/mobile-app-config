---
name: android-mobile-config-help
description: Quick reference for android-mobile-config commands and local usage. Use when the user says "/android-mobile-config-help", "/android-mobile-config help", "android mobile config help", "what android-mobile-config commands exist", or asks how to use the Android Mobile Config skill.
---

# Android Mobile Config Help

Display this quick reference. One-shot only; do not change files unless the user asks.

| Command | Purpose |
|---|---|
| `/android-mobile-config` | General skill entry and routing |
| `/android-mobile-config-init` | Create `android-mobile-config.json` |
| `/android-mobile-config-flavors` | Configure Android product flavors |
| `/android-mobile-config-assets` | Generate Android app assets |
| `/android-mobile-config-network-security` | Configure optional network-security XML |

Direct CLI form from an Android project root:

```bash
~/.codex/skills/android-mobile-config/scripts/android-mobile-config flavors
~/.codex/skills/android-mobile-config/scripts/android-mobile-config assets
~/.codex/skills/android-mobile-config/scripts/android-mobile-config network-security
```

