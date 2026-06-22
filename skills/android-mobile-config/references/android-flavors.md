# Android Flavors

Flavor configuration targets Kotlin Gradle Android app modules first.

Rules:

- Preserve unrelated Gradle sections.
- Preserve user-defined flavors that are not named in config.
- Keep repeated runs idempotent.
- Do not configure network security during flavor setup.
- Create `app_name` resources under `src/<flavor>/res/values/strings.xml`.

Validation should confirm configured flavors, flavor dimension, BuildConfig fields, and expected Gradle task names.

