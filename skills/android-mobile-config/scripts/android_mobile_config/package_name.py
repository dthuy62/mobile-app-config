from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

from .config import ConfigError, config_path, write_config
from .gradle_kts import find_block_range, infer_application_id

KEYWORDS = {
    "abstract",
    "assert",
    "boolean",
    "break",
    "byte",
    "case",
    "catch",
    "char",
    "class",
    "const",
    "continue",
    "default",
    "do",
    "double",
    "else",
    "enum",
    "extends",
    "final",
    "finally",
    "float",
    "for",
    "goto",
    "if",
    "implements",
    "import",
    "instanceof",
    "int",
    "interface",
    "long",
    "native",
    "new",
    "package",
    "private",
    "protected",
    "public",
    "return",
    "short",
    "static",
    "strictfp",
    "super",
    "switch",
    "synchronized",
    "this",
    "throw",
    "throws",
    "transient",
    "try",
    "void",
    "volatile",
    "while",
    "as",
    "fun",
    "in",
    "is",
    "object",
    "typealias",
    "val",
    "var",
    "when",
}


def is_valid_application_id(value: str) -> bool:
    parts = value.split(".")
    return bool(value) and all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", part) and part not in KEYWORDS for part in parts)


def configure_package_name(root: Path, config: dict[str, Any], application_id: str | None) -> str:
    target = application_id or config.get("packageName", {}).get("applicationId", "")
    if not is_valid_application_id(target):
        raise ConfigError(f"Invalid applicationId: {target}")
    gradle_path = root / config["module"] / "build.gradle.kts"
    if not gradle_path.exists():
        raise ConfigError(f"Missing Kotlin Gradle file: {gradle_path}")
    gradle_text = gradle_path.read_text()
    old_application_id = infer_application_id(root, config)
    src = root / config["module"] / "src"
    old_source_package = old_application_id
    sync_source_packages = config.get("packageName", {}).get("syncSourcePackages", True)
    if sync_source_packages and source_files(src):
        old_source_package = resolve_source_package(extract_namespace(gradle_text), source_package_declarations(src))
    updated_gradle_text = update_gradle_package(gradle_text, target)
    if sync_source_packages:
        sync_sources(src, old_source_package, target)
    gradle_path.write_text(updated_gradle_text)
    config.setdefault("packageName", {})["applicationId"] = target
    write_config(config_path(root), config)
    return f"package name configured: {old_application_id} -> {target}"


def validate_package_name(root: Path, config: dict[str, Any]) -> list[str]:
    target = config.get("packageName", {}).get("applicationId", "") or infer_application_id(root, config)
    errors: list[str] = []
    if not is_valid_application_id(target):
        return [f"Invalid applicationId: {target}"]
    gradle_path = root / config["module"] / "build.gradle.kts"
    if not gradle_path.exists():
        return [f"Missing Kotlin Gradle file: {gradle_path}"]
    text = gradle_path.read_text()
    try:
        application_id = infer_application_id(root, config)
    except ConfigError as exc:
        errors.append(str(exc))
        application_id = ""
    if application_id != target:
        errors.append(f"applicationId does not match {target}")
    if extract_namespace(text) != target:
        errors.append(f"namespace does not match {target}")
    src = root / config["module"] / "src"
    files = source_files(src)
    packages = source_package_declarations(src)
    if config.get("packageName", {}).get("syncSourcePackages", True) and files and not packages:
        errors.append("No source package declarations found")
    for path in files:
        for line in path.read_text().splitlines():
            match = re.match(r"\s*package\s+([A-Za-z_][\w.]*);?", line)
            if match and not (match.group(1) == target or match.group(1).startswith(target + ".")):
                errors.append(f"Stale package declaration in {path}")
                break
    return errors


def extract_namespace(text: str) -> str | None:
    match = re.search(r'namespace\s*=\s*"([^"]+)"', text)
    return match.group(1) if match else None


def source_package_declarations(src: Path) -> list[str]:
    packages: list[str] = []
    for path in source_files(src):
        for line in path.read_text().splitlines():
            match = re.match(r"\s*package\s+([A-Za-z_][\w.]*);?", line)
            if match:
                packages.append(match.group(1))
                break
    return packages


def resolve_source_package(namespace: str | None, packages: list[str]) -> str:
    if not packages:
        raise ConfigError("Cannot infer source package: no source package declarations found")
    if namespace and any(package_is_under(package, namespace) for package in packages):
        if all(package_is_under(package, namespace) for package in packages):
            return namespace
        detail = ", ".join(sorted(set(packages)))
        raise ConfigError(f"Cannot infer source package from declarations: {detail}")
    common = common_package_prefix(packages)
    if common:
        return common
    detail = ", ".join(sorted(set(packages)))
    raise ConfigError(f"Cannot infer source package from declarations: {detail}")


def package_is_under(package: str, root: str) -> bool:
    return package == root or package.startswith(root + ".")


def common_package_prefix(packages: list[str]) -> str | None:
    split = [package.split(".") for package in packages]
    common: list[str] = []
    for parts in zip(*split):
        if len(set(parts)) != 1:
            break
        common.append(parts[0])
    if len(common) < 2:
        return None
    root = ".".join(common)
    if all(package_is_under(package, root) for package in packages):
        return root
    return None


def update_gradle_package(text: str, application_id: str) -> str:
    if re.search(r'namespace\s*=', text):
        text = re.sub(r'namespace\s*=\s*"[^"]+"', f'namespace = "{application_id}"', text, count=1)
    else:
        android = find_block_range(text, "android")
        if android is None:
            raise ConfigError("Cannot find android block")
        _start, open_index, _close_index = android
        text = text[: open_index + 1] + f'\n  namespace = "{application_id}"' + text[open_index + 1 :]
    block = find_block_range(text, "defaultConfig")
    if block is None:
        raise ConfigError("Cannot find android.defaultConfig block")
    _start, open_index, close_index = block
    body = text[open_index + 1 : close_index]
    if re.search(r'applicationId\s*=', body):
        body = re.sub(r'applicationId\s*=\s*"[^"]+"', f'applicationId = "{application_id}"', body, count=1)
    else:
        body = body.rstrip() + f'\n    applicationId = "{application_id}"\n  '
    return text[: open_index + 1] + body + text[close_index:]


def sync_sources(src: Path, old: str, new: str) -> None:
    if not src.exists() or old == new:
        rewrite_source_packages(src, old, new)
        return
    old_parts = old.split(".")
    new_parts = new.split(".")
    for source_root in list(src.glob("*/java")) + list(src.glob("*/kotlin")):
        old_dir = source_root.joinpath(*old_parts)
        new_dir = source_root.joinpath(*new_parts)
        if old_dir.exists() and old_dir != new_dir:
            merge_move(old_dir, new_dir)
            prune_empty(old_dir.parent, source_root)
    rewrite_source_packages(src, old, new)


def merge_move(old_dir: Path, new_dir: Path) -> None:
    new_dir.mkdir(parents=True, exist_ok=True)
    for child in old_dir.iterdir():
        target = new_dir / child.name
        if child.is_dir() and target.exists():
            merge_move(child, target)
        else:
            shutil.move(str(child), str(target))
    old_dir.rmdir()


def prune_empty(path: Path, stop: Path) -> None:
    while path != stop and path.exists():
        try:
            path.rmdir()
        except OSError:
            return
        path = path.parent


def rewrite_source_packages(src: Path, old: str, new: str) -> None:
    old_re = re.escape(old)
    for path in source_files(src):
        text = path.read_text()
        text = re.sub(rf"(^\s*package\s+){old_re}(\b|\.)", rf"\g<1>{new}\2", text, flags=re.MULTILINE)
        text = re.sub(rf"(^\s*import\s+){old_re}(\b|\.)", rf"\g<1>{new}\2", text, flags=re.MULTILINE)
        path.write_text(text)


def source_files(src: Path) -> list[Path]:
    if not src.exists():
        return []
    return [
        path
        for path in src.rglob("*")
        if path.suffix in {".kt", ".java"} and not any(part in {"build", ".gradle", "generated"} for part in path.parts)
    ]
