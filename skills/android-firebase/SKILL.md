---
name: android-firebase
description: Configure Firebase multi-flavor google-services.json files with mobile-app-config. Use when the user says "/android-firebase", "/mobile-app-config firebase", "android mobile config firebase", or asks to set up Firebase for Android flavors.
---

# Mobile App Config Firebase

Configure Firebase from the Android project root. The command uses Firebase CLI local login only.

If Firebase CLI is not logged in, stop and tell the user:

```bash
firebase login
```

Then rerun the same `mobile-app-config firebase` command.

Single Firebase project for all flavors:

```bash
~/.codex/skills/android/scripts/mobile-app-config firebase --mode single --project my-firebase
```

One Firebase project per flavor:

```bash
~/.codex/skills/android/scripts/mobile-app-config firebase --mode per-flavor --flavor dev=my-dev --flavor prod=my-prod
```

Create missing Firebase Android apps only when explicitly requested:

```bash
~/.codex/skills/android/scripts/mobile-app-config firebase --mode single --project my-firebase --create-apps
```

Then validate:

```bash
~/.codex/skills/android/scripts/mobile-app-config validate-firebase
```

Do not store Firebase credentials, service account JSON, or tokens in `android-app-config.json`.
