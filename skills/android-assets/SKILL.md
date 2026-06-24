---
name: android-assets
description: Generate or validate Android app icons and splash screen resources with mobile-app-config. Use when the user says "/android-assets", "/mobile-app-config assets", "android mobile config assets", or asks to generate Android app icons, adaptive icons, themed icons, or splash screens.
---

# Mobile App Config Assets

Generate Android assets from the project root. Passing asset options stores them in `android-app-config.json`.

Use the bundled CLI at `../android/scripts/mobile-app-config`, resolved relative to this `SKILL.md`. Run it with cwd set to the Android project root.

```bash
mobile-app-config assets --type app-icons --image branding/logo.png
mobile-app-config assets --type splash-screens --image branding/splash.png
mobile-app-config assets --type all --image branding/logo.png
```

Then validate:

```bash
mobile-app-config validate-assets --type all
```

Asset generation is disabled by default. Passing `--image` enables the selected type. Existing `assets.sourceIcon` remains supported for older configs.

Splash resources use Android 12+ platform attrs and Android 11-and-below `windowBackground`. This plugin does not add AndroidX SplashScreen or call `installSplashScreen()`.
