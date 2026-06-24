---
name: android-firebase
description: Configure Firebase multi-flavor google-services.json files with mobile-app-config. Use when the user says "/android-firebase", "/mobile-app-config firebase", "android mobile config firebase", or asks to set up Firebase for Android flavors.
---

# Mobile App Config Firebase

Configure Firebase from the Android project root. The command uses Firebase CLI local login only.
Resolve `../android/scripts/mobile-app-config` relative to this `SKILL.md`, then run it from the Android project root.

If Firebase CLI is not logged in, stop and tell the user:

```bash
firebase login
```

Then rerun the same `mobile-app-config firebase` command.

Single Firebase project for all flavors:

```bash
<resolved-script> firebase --mode single --project my-firebase
```

One Firebase project per flavor:

```bash
<resolved-script> firebase --mode per-flavor --flavor dev=my-dev --flavor prod=my-prod
```

Create missing Firebase Android apps only when explicitly requested:

```bash
<resolved-script> firebase --mode single --project my-firebase --create-apps
```

Then validate:

```bash
<resolved-script> validate-firebase
```

Do not store Firebase credentials, service account JSON, or tokens in `android-app-config.json`.
