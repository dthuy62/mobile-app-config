---
name: android-mobile-config-assets
description: Generate or validate Android launcher, adaptive, splash, and notification assets with android-mobile-config. Use when the user says "/android-mobile-config-assets", "/android-mobile-config assets", "android mobile config assets", or asks to generate Android app icons, splash assets, adaptive icons, or notification icons.
---

# Android Mobile Config Assets

Generate Android assets from the project root. If `android-mobile-config.json` is missing, the script auto-creates it first.

Run the canonical skill CLI from the Android project root:

```bash
~/.codex/skills/android-mobile-config/scripts/android-mobile-config assets
```

Then validate:

```bash
~/.codex/skills/android-mobile-config/scripts/android-mobile-config validate-assets
```

Asset generation is disabled by default. Enable `assets.enabled=true` and set `assets.sourceIcon` before expecting generated images.
