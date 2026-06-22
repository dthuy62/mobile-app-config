from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

CONFIG_NAME = "android-mobile-config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "module": "app",
    "dimension": "environment",
    "flavors": {
        "dev": {
            "applicationIdSuffix": ".dev",
            "appName": "[DEV] Career Ops",
            "buildConfigFields": {
                "CAREER_OPS_ENVIRONMENT": "dev",
                "CAREER_OPS_DEFAULT_BASE_URL": "http://10.0.2.2:3000",
            },
        },
        "prod": {
            "applicationIdSuffix": "",
            "appName": "Career Ops",
            "buildConfigFields": {
                "CAREER_OPS_ENVIRONMENT": "prod",
                "CAREER_OPS_DEFAULT_BASE_URL": "",
            },
        },
    },
    "networkSecurity": {"enabled": False},
    "firebase": {
        "enabled": False,
        "mode": "single",
        "project": "",
        "createApps": False,
        "flavors": {
            "dev": {"project": ""},
            "prod": {"project": ""},
        },
    },
    "assets": {
        "enabled": False,
        "sourceIcon": "",
        "generateLauncherIcon": True,
        "generateAdaptiveIcon": True,
        "generateSplashIcon": True,
        "generateNotificationIcon": True,
    },
}


class ConfigError(RuntimeError):
    pass


def config_path(root: Path) -> Path:
    return root / CONFIG_NAME


def load_or_init(root: Path, *, force: bool = False) -> tuple[dict[str, Any], bool]:
    path = config_path(root)
    if path.exists() and not force:
        return load_config(path), False
    config = infer_config(root)
    write_config(path, config)
    return config, True


def load_config(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError(f"{path} must contain a JSON object")
    return normalize_config(raw)


def write_config(path: Path, config: dict[str, Any]) -> None:
    path.write_text(json.dumps(normalize_config(config), indent=2, sort_keys=False) + "\n")


def normalize_config(raw: dict[str, Any]) -> dict[str, Any]:
    config = deepcopy(DEFAULT_CONFIG)
    deep_update(config, raw)
    if not isinstance(config.get("flavors"), dict) or not config["flavors"]:
        raise ConfigError("Config must define at least one flavor")
    return config


def deep_update(target: dict[str, Any], source: dict[str, Any]) -> None:
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_update(target[key], value)
        else:
            target[key] = value


def infer_config(root: Path) -> dict[str, Any]:
    config = deepcopy(DEFAULT_CONFIG)
    module = infer_module(root)
    config["module"] = module
    gradle_path = root / module / "build.gradle.kts"
    if not gradle_path.exists():
        return config

    text = gradle_path.read_text()
    dimension = infer_dimension(text)
    if dimension:
        config["dimension"] = dimension

    app_name = infer_app_name(root, module) or config["flavors"]["prod"]["appName"]
    flavors = infer_flavors(text, app_name)
    if flavors:
        config["flavors"] = flavors
    else:
        config["flavors"]["prod"]["appName"] = app_name
        config["flavors"]["dev"]["appName"] = f"[DEV] {app_name}"
    return config


def infer_module(root: Path) -> str:
    if (root / "app" / "build.gradle.kts").exists():
        return "app"
    for path in sorted(root.glob("*/build.gradle.kts")):
        return path.parent.name
    return "app"


def infer_dimension(text: str) -> str | None:
    patterns = [
        r'flavorDimensions\s*\+=\s*"([^"]+)"',
        r'flavorDimensions\s*\(\s*"([^"]+)"\s*\)',
        r'flavorDimensions\.add\s*\(\s*"([^"]+)"\s*\)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def infer_flavors(text: str, app_name: str) -> dict[str, Any]:
    product_flavors = find_plain_block(text, "productFlavors")
    if product_flavors is None:
        return {}
    flavors: dict[str, Any] = {}
    for name, block in find_named_blocks(product_flavors, "create"):
        suffix = ""
        suffix_match = re.search(r'applicationIdSuffix\s*=\s*"([^"]*)"', block)
        if suffix_match:
            suffix = suffix_match.group(1)
        fields: dict[str, str] = {}
        for field_match in re.finditer(
            r'buildConfigField\s*\(\s*"String"\s*,\s*"([^"]+)"\s*,\s*"((?:\\"|[^"])*)"\s*\)',
            block,
        ):
            fields[field_match.group(1)] = _unquote_kotlin_string(field_match.group(2))
        flavor_app_name = app_name if name == "prod" else f"[{name.upper()}] {app_name}"
        flavors[name] = {
            "applicationIdSuffix": suffix,
            "appName": flavor_app_name,
            "buildConfigFields": fields,
        }
    return flavors


def find_plain_block(text: str, name: str) -> str | None:
    match = re.search(rf"\b{re.escape(name)}\s*\{{", text)
    if not match:
        return None
    open_index = text.find("{", match.start())
    end = find_matching_brace(text, open_index)
    if end == -1:
        return None
    return text[open_index + 1 : end]


def find_named_blocks(text: str, function_name: str) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    pattern = re.compile(rf'{re.escape(function_name)}\("([^"]+)"\)\s*\{{')
    for match in pattern.finditer(text):
        start = match.end() - 1
        end = find_matching_brace(text, start)
        if end != -1:
            results.append((match.group(1), text[start + 1 : end]))
    return results


def find_matching_brace(text: str, open_index: int) -> int:
    depth = 0
    in_string = False
    escaped = False
    for index in range(open_index, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return -1


def infer_app_name(root: Path, module: str) -> str | None:
    strings_path = root / module / "src" / "main" / "res" / "values" / "strings.xml"
    if not strings_path.exists():
        return None
    match = re.search(
        r'<string\s+name="app_name"\s*>(.*?)</string>',
        strings_path.read_text(),
        re.DOTALL,
    )
    if not match:
        return None
    return match.group(1).strip()


def _unquote_kotlin_string(value: str) -> str:
    if value.startswith('\\"') and value.endswith('\\"'):
        return value[2:-2]
    return value.replace('\\"', '"')
