from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .config import ConfigError


def configure_network_security(root: Path, config: dict[str, Any]) -> str:
    network = config.get("networkSecurity", {})
    if not network.get("enabled", False):
        return "network security disabled; no changes made"
    target_flavors = network.get("targetFlavors") or ["dev"]
    allow_prod = network.get("allowProdCleartext", False)
    if "prod" in target_flavors and network.get("cleartextTrafficPermitted", False) and not allow_prod:
        raise ConfigError("Refusing broad cleartext traffic for prod without allowProdCleartext=true")

    module = config["module"]
    for flavor in target_flavors:
        xml_dir = root / module / "src" / flavor / "res" / "xml"
        xml_dir.mkdir(parents=True, exist_ok=True)
        (xml_dir / "network_security_config.xml").write_text(render_network_security(network))
        manifest_path = root / module / "src" / flavor / "AndroidManifest.xml"
        write_manifest_reference(manifest_path)
    return "network security configured"


def validate_network_security(root: Path, config: dict[str, Any]) -> list[str]:
    network = config.get("networkSecurity", {})
    if not network.get("enabled", False):
        return []
    module = config["module"]
    errors: list[str] = []
    for flavor in network.get("targetFlavors") or ["dev"]:
        xml_path = root / module / "src" / flavor / "res" / "xml" / "network_security_config.xml"
        manifest_path = root / module / "src" / flavor / "AndroidManifest.xml"
        if not xml_path.exists():
            errors.append(f"Missing network security XML for {flavor}")
        if not manifest_path.exists() or "android:networkSecurityConfig" not in manifest_path.read_text():
            errors.append(f"Missing manifest network security reference for {flavor}")
    return errors


def render_network_security(network: dict[str, Any]) -> str:
    cleartext = "true" if network.get("cleartextTrafficPermitted", True) else "false"
    domains = network.get("domains") or ["10.0.2.2", "localhost"]
    domain_lines = "\n".join(f"        <domain>{domain}</domain>" for domain in domains)
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<network-security-config>\n"
        f'    <domain-config cleartextTrafficPermitted="{cleartext}">\n'
        f"{domain_lines}\n"
        "    </domain-config>\n"
        "</network-security-config>\n"
    )


def write_manifest_reference(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    attr = 'android:networkSecurityConfig="@xml/network_security_config"'
    if not path.exists():
        path.write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<manifest xmlns:android="http://schemas.android.com/apk/res/android">\n'
            f"    <application {attr} />\n"
            "</manifest>\n"
        )
        return
    text = path.read_text()
    if attr in text:
        return
    if "android:networkSecurityConfig=" in text:
        text = re.sub(r'\sandroid:networkSecurityConfig="[^"]+"', f" {attr}", text)
    else:
        text = re.sub(r"<application\b", f"<application {attr}", text, count=1)
    path.write_text(text)

