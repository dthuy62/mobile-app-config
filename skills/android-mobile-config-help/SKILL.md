---
name: android-mobile-config-help
description: Quick reference for android-mobile-config commands and local usage. Use when the user says "/android-mobile-config-help", "/android-mobile-config help", "android mobile config help", "what android-mobile-config commands exist", or asks how to use the Mobile App Config skill.
---

# Mobile App Config Help

Display this quick reference. One-shot only; do not change files unless the user asks.

| Command | Purpose |
|---|---|
| `/android-mobile-config` | General skill entry and routing |
| `/android-mobile-config-init` | Create `android-mobile-config.json` |
| `/android-mobile-config-flavors` | Configure Android product flavors |
| `/android-mobile-config-firebase` | Configure Firebase multi-flavor `google-services.json` |
| `/android-mobile-config-assets` | Generate Android app assets |
| `/android-mobile-config-network-security` | Configure optional network-security XML |

Direct CLI form from an Android project root:

```bash
~/.codex/skills/android-mobile-config/scripts/android-mobile-config flavors
~/.codex/skills/android-mobile-config/scripts/android-mobile-config firebase --mode single --project my-firebase
~/.codex/skills/android-mobile-config/scripts/android-mobile-config firebase --mode per-flavor --flavor dev=my-dev --flavor prod=my-prod
~/.codex/skills/android-mobile-config/scripts/android-mobile-config assets
~/.codex/skills/android-mobile-config/scripts/android-mobile-config network-security
```

After flavor generation, run Gradle Sync in Android Studio. Expected variants are `devDebug`, `prodDebug`, `devRelease`, and `prodRelease`.

Splash generation uses Android 12+ platform attrs and Android 11-and-below `windowBackground`; it does not add AndroidX SplashScreen.
