from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .config import ConfigError
from .resources import write_flavor_app_names

GOOGLE_SERVICES_PLUGIN = 'id("com.google.gms.google-services")'
GOOGLE_SERVICES_ROOT_PLUGIN = f'{GOOGLE_SERVICES_PLUGIN} version "4.5.0" apply false'


def configure_flavors(root: Path, config: dict[str, Any]) -> list[str]:
    module = config["module"]
    gradle_path = root / module / "build.gradle.kts"
    if not gradle_path.exists():
        raise ConfigError(f"Missing Kotlin Gradle file: {gradle_path}")
    text = gradle_path.read_text()
    text = ensure_flavor_dimension(text, config["dimension"])
    text = ensure_product_flavors(text, config)
    gradle_path.write_text(text)
    write_flavor_app_names(root, config)
    return expected_tasks(config)


def validate_flavors(root: Path, config: dict[str, Any]) -> list[str]:
    module = config["module"]
    gradle_path = root / module / "build.gradle.kts"
    errors: list[str] = []
    if not gradle_path.exists():
        return [f"Missing Kotlin Gradle file: {gradle_path}"]
    text = gradle_path.read_text()
    if config["dimension"] not in text:
        errors.append(f"Missing flavor dimension {config['dimension']!r}")
    for flavor, flavor_config in config["flavors"].items():
        if f'create("{flavor}")' not in text:
            errors.append(f"Missing flavor {flavor!r}")
        suffix = flavor_config.get("applicationIdSuffix", "")
        if suffix and f'applicationIdSuffix = "{suffix}"' not in text:
            errors.append(f"Missing applicationIdSuffix for {flavor!r}")
        for key, value in flavor_config.get("buildConfigFields", {}).items():
            escaped = str(value).replace('"', '\\"')
            if f'buildConfigField("String", "{key}", "\\"{escaped}\\"")' not in text:
                errors.append(f"Missing BuildConfig field {key!r} for {flavor!r}")
        strings_path = root / module / "src" / flavor / "res" / "values" / "strings.xml"
        if not strings_path.exists():
            errors.append(f"Missing app_name resource for {flavor!r}")
    return errors


def ensure_google_services_gradle(root: Path, config: dict[str, Any]) -> None:
    root_gradle = root / "build.gradle.kts"
    app_gradle = root / config["module"] / "build.gradle.kts"
    if not root_gradle.exists():
        raise ConfigError(f"Missing Kotlin Gradle file: {root_gradle}")
    if not app_gradle.exists():
        raise ConfigError(f"Missing Kotlin Gradle file: {app_gradle}")
    root_gradle.write_text(ensure_plugin(root_gradle.read_text(), GOOGLE_SERVICES_ROOT_PLUGIN))
    app_gradle.write_text(ensure_plugin(app_gradle.read_text(), GOOGLE_SERVICES_PLUGIN))


def validate_google_services_gradle(root: Path, config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    root_gradle = root / "build.gradle.kts"
    app_gradle = root / config["module"] / "build.gradle.kts"
    if not root_gradle.exists():
        errors.append(f"Missing Kotlin Gradle file: {root_gradle}")
    elif GOOGLE_SERVICES_PLUGIN not in root_gradle.read_text():
        errors.append("Missing Google Services plugin in root build.gradle.kts")
    if not app_gradle.exists():
        errors.append(f"Missing Kotlin Gradle file: {app_gradle}")
    elif GOOGLE_SERVICES_PLUGIN not in app_gradle.read_text():
        errors.append("Missing Google Services plugin in app build.gradle.kts")
    return errors


def expected_tasks(config: dict[str, Any]) -> list[str]:
    return [f"assemble{flavor[:1].upper()}{flavor[1:]}Debug" for flavor in config["flavors"]]


def infer_application_id(root: Path, config: dict[str, Any]) -> str:
    gradle_path = root / config["module"] / "build.gradle.kts"
    if not gradle_path.exists():
        raise ConfigError(f"Missing Kotlin Gradle file: {gradle_path}")
    text = gradle_path.read_text()
    block_range = find_block_range(text, "defaultConfig")
    if block_range is None:
        raise ConfigError("Cannot find android.defaultConfig block")
    _start, open_index, close_index = block_range
    default_config = text[open_index + 1 : close_index]
    match = re.search(r'applicationId\s*=\s*"([^"]+)"', default_config)
    if not match:
        raise ConfigError("Cannot infer defaultConfig.applicationId")
    return match.group(1)


def package_names(root: Path, config: dict[str, Any]) -> dict[str, str]:
    application_id = infer_application_id(root, config)
    packages: dict[str, str] = {}
    for flavor, flavor_config in config["flavors"].items():
        packages[flavor] = application_id + flavor_config.get("applicationIdSuffix", "")
    return packages


def ensure_plugin(text: str, plugin_line: str) -> str:
    if plugin_line in text or plugin_line.split(" version ", 1)[0] in text:
        return text
    block_range = find_block_range(text, "plugins")
    if block_range is None:
        return f"plugins {{\n  {plugin_line}\n}}\n\n{text}"
    _start, open_index, close_index = block_range
    body = text[open_index + 1 : close_index].rstrip()
    indent = "  "
    return text[: open_index + 1] + body + f"\n{indent}{plugin_line}\n" + text[close_index:]


def ensure_flavor_dimension(text: str, dimension: str) -> str:
    if re.search(r"flavorDimensions\s*\+=", text):
        return text
    default_match = re.search(r"\n\s*defaultConfig\s*\{", text)
    if not default_match:
        raise ConfigError("Cannot find android.defaultConfig block")
    open_index = text.find("{", default_match.start())
    close_index = find_matching_brace(text, open_index)
    if close_index == -1:
        raise ConfigError("Cannot parse android.defaultConfig block")
    insert = f'\n\n  flavorDimensions += "{dimension}"'
    return text[: close_index + 1] + insert + text[close_index + 1 :]


def ensure_product_flavors(text: str, config: dict[str, Any]) -> str:
    block_range = find_block_range(text, "productFlavors")
    if block_range is None:
        dimension_match = re.search(r'^\s*flavorDimensions\s*\+=\s*"[^"]+"\s*$', text, re.MULTILINE)
        if not dimension_match:
            raise ConfigError("Cannot find flavorDimensions line")
        block = "\n\n  productFlavors {\n" + "".join(render_flavor(name, config) for name in config["flavors"]) + "  }"
        return text[: dimension_match.end()] + block + text[dimension_match.end() :]

    start, open_index, close_index = block_range
    body = text[open_index + 1 : close_index]
    for flavor in config["flavors"]:
        existing = find_create_block_range(body, flavor)
        rendered = render_flavor(flavor, config)
        if existing is None:
            body = body.rstrip() + "\n" + rendered
        else:
            body = body[: existing[0]] + rendered.rstrip("\n") + body[existing[2] + 1 :]
    return text[: open_index + 1] + body.rstrip() + "\n  " + text[close_index:]


def render_flavor(name: str, config: dict[str, Any]) -> str:
    flavor = config["flavors"][name]
    lines = [f'    create("{name}") {{', f'      dimension = "{config["dimension"]}"']
    suffix = flavor.get("applicationIdSuffix", "")
    if suffix:
        lines.append(f'      applicationIdSuffix = "{suffix}"')
    for key, value in flavor.get("buildConfigFields", {}).items():
        escaped = str(value).replace('"', '\\"')
        lines.append(f'      buildConfigField("String", "{key}", "\\"{escaped}\\"")')
    lines.append("    }")
    return "\n".join(lines) + "\n"


def find_block_range(text: str, name: str) -> tuple[int, int, int] | None:
    match = re.search(rf"\b{re.escape(name)}\s*\{{", text)
    if not match:
        return None
    open_index = text.find("{", match.start())
    close_index = find_matching_brace(text, open_index)
    if close_index == -1:
        raise ConfigError(f"Cannot parse {name} block")
    return match.start(), open_index, close_index


def find_create_block_range(text: str, flavor: str) -> tuple[int, int, int] | None:
    match = re.search(rf'^[ \t]*create\("{re.escape(flavor)}"\)\s*\{{', text, re.MULTILINE)
    if not match:
        return None
    open_index = text.find("{", match.start())
    close_index = find_matching_brace(text, open_index)
    if close_index == -1:
        raise ConfigError(f"Cannot parse flavor block {flavor}")
    return match.start(), open_index, close_index


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
