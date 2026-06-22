# Network Security

Network security is disabled by default.

Rules:

- Do nothing when `networkSecurity.enabled=false`.
- Only create XML and manifest references when explicitly enabled.
- Target selected flavors when configured.
- Refuse broad cleartext traffic for `prod` unless `allowProdCleartext=true` is explicitly set.

Prefer flavor-specific manifests so local development settings do not leak into production.

