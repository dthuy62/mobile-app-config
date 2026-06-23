---
name: android-mobile-config-network-security
description: Configure optional Android network-security XML for local or dev builds with android-mobile-config. Use when the user says "/android-mobile-config-network-security", "/android-mobile-config network-security", "android mobile config network security", or asks to allow local HTTP, 10.0.2.2, localhost, or flavor-specific Android network security config.
---

# Mobile App Config Network Security

Configure Android network security from the project root. If `android-mobile-config.json` is missing, the script auto-creates it first.

Run the canonical skill CLI from the Android project root:

```bash
~/.codex/skills/android-mobile-config/scripts/android-mobile-config network-security
```

Then validate:

```bash
~/.codex/skills/android-mobile-config/scripts/android-mobile-config validate-network-security
```

Network security is disabled by default. Do not enable broad cleartext for `prod` unless the user explicitly requests it.
