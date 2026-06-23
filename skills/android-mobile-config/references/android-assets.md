# Android Assets

Asset generation is disabled by default. Passing `--image` enables the selected asset type and stores project-relative paths in `android-mobile-config.json`.

```bash
android-mobile-config assets --type app-icons --image branding/logo.png
android-mobile-config assets --type splash-screens --image branding/splash.png
android-mobile-config assets --type all --image branding/logo.png
```

## App Icons

`--type app-icons` generates Android launcher assets for old and modern Android:

- legacy launcher PNGs in density-specific `mipmap-*` folders
- adaptive icon foreground/background resources in `drawable`
- adaptive icon XML in `mipmap-anydpi-v26`
- optional monochrome themed icon when `--monochrome-image` is provided

The source image must be at least 432x432 pixels. The generator pads and resizes; it does not crop.

## Splash Screens

`--type splash-screens` generates XML-only splash resources:

- Android 12+ platform splash attrs in `values-v31`
- legacy pre-12 `windowBackground` layer-list in `drawable`
- optional night resources when `--dark-image` or `--dark-background-color` is provided
- launcher Activity manifest theme, falling back to the application theme when no launcher Activity exists

Android 12+ platform splash screens are icon plus background, not full-screen artwork. This command does not patch Kotlin or Java, does not add AndroidX SplashScreen, and does not call `installSplashScreen()`.

Use Pillow for image processing. If Pillow is unavailable, fail with an install hint instead of silently producing incomplete assets.
