---
name: android-assets
description: Generate or validate Android app icons and splash screen resources with mobile-app-config. Use when the user says "/android-assets", "/mobile-app-config assets", "android mobile config assets", or asks to generate Android app icons, adaptive icons, themed icons, or splash screens.
---

# Mobile App Config Assets

Generate Android assets from the project root. Passing asset options stores them in `android-app-config.json`.

Resolve `../android/scripts/mobile-app-config` relative to this `SKILL.md`, then run it from the Android project root:

```bash
<resolved-script> assets --type app-icons --image branding/logo.png
<resolved-script> assets --type splash-screens --image branding/splash.png
<resolved-script> assets --type all --image branding/logo.png
```

Then validate:

```bash
<resolved-script> validate-assets --type all
```

Asset generation is disabled by default. Passing `--image` enables the selected type. Existing `assets.sourceIcon` remains supported for older configs.

Splash resources use Android 12+ platform attrs and Android 11-and-below `windowBackground`. This plugin does not add AndroidX SplashScreen or call `installSplashScreen()`.
