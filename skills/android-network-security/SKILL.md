---
name: android-network-security
description: Configure optional Android network-security XML for local or dev builds with mobile-app-config. Use when the user says "/android-network-security", "/mobile-app-config network-security", "android mobile config network security", or asks to allow local HTTP, 10.0.2.2, localhost, or flavor-specific Android network security config.
---

# Mobile App Config Network Security

Configure Android network security from the project root. Missing config is inferred in memory.

Use the bundled CLI at `../android/scripts/mobile-app-config`, resolved relative to this `SKILL.md`. Run it with cwd set to the Android project root.

```bash
mobile-app-config network-security
```

Then validate:

```bash
mobile-app-config validate-network-security
```

Network security is disabled by default. Do not enable broad cleartext for `prod` unless the user explicitly requests it.
