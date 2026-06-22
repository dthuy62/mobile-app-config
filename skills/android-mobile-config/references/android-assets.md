# Android Assets

Asset generation is disabled by default.

When enabled, `assets.sourceIcon` is required. The source image should be at least 432x432 pixels so xxxhdpi launcher icons can be generated cleanly.

Generated resources may include:

- launcher icons in density-specific `mipmap-*` folders
- adaptive icon XML in `mipmap-anydpi-v26`
- splash icon drawable
- notification icon drawable

Use Pillow for image processing. If Pillow is unavailable, fail with an install hint instead of silently producing incomplete assets.

