---
name: android-help
description: Quick reference for mobile-app-config commands and local usage. Use when the user says "/android-help", "/mobile-app-config help", "android mobile config help", "what mobile-app-config commands exist", or asks how to use the Mobile App Config skill.
---

# Mobile App Config Help

Display this quick reference. One-shot only; do not change files unless the user asks.

| Command | Purpose |
|---|---|
| `/mobile-app-config` | General skill entry and routing |
| `/android-init` | Create `android-app-config.json` |
| `/android-flavors` | Configure Android product flavors |
| `/android-firebase` | Configure Firebase multi-flavor `google-services.json` |
| `/android-assets` | Generate Android app assets |
| `/android-network-security` | Configure optional network-security XML |

Direct CLI form from an Android project root:

```bash
~/.codex/skills/android/scripts/mobile-app-config flavors
~/.codex/skills/android/scripts/mobile-app-config firebase --mode single --project my-firebase
~/.codex/skills/android/scripts/mobile-app-config firebase --mode per-flavor --flavor dev=my-dev --flavor prod=my-prod
~/.codex/skills/android/scripts/mobile-app-config assets
~/.codex/skills/android/scripts/mobile-app-config network-security
```

After flavor generation, run Gradle Sync in Android Studio. Expected variants are `devDebug`, `prodDebug`, `devRelease`, and `prodRelease`.

Splash generation uses Android 12+ platform attrs and Android 11-and-below `windowBackground`; it does not add AndroidX SplashScreen.
