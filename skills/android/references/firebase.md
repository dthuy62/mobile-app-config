# Firebase

Firebase setup uses Firebase CLI local login.

Rules:

- Require `firebase-tools`; fail with an install hint when the `firebase` command is missing.
- Check auth with `firebase projects:list --json`.
- If auth fails, stop and tell the user to run `firebase login`, then rerun the same command.
- Do not read, write, or store service account JSON, CI tokens, or Firebase auth tokens.
- `single` mode writes `app/google-services.json` with one client per package name.
- `per-flavor` mode writes `app/src/<flavor>/google-services.json`.
- Create Firebase Android apps only when `createApps=true` or `--create-apps` is passed.
- Add the Google Services Gradle plugin idempotently to root and app Kotlin Gradle files.
- Validation checks expected files, package names, and Gradle plugin wiring.
