from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


Warn = Callable[[str], None]


@dataclass(frozen=True)
class ExportOptions:
    json_file: Path
    output: Path
    token_type: str = "colors"
    layer: str = "auto"
    base_json: Path | None = None
    class_prefix: str = "App"
    base_class: str = "AppColorBase"
    base_import: str = "app_color_base.dart"
    light_mode: str = "light"
    dark_mode: str = "dark"
    exclude_material_extension: bool = False
    strict: bool = True
    dry_run: bool = False


@dataclass(frozen=True)
class Variable:
    id: str
    name: str
    resolved_type: str
    values_by_mode: dict[str, Any]
    modes: dict[str, str]
    alias_target_name: str | None = None


@dataclass(frozen=True)
class ColorToken:
    field: str
    group: str
    source_name: str
    values_by_mode_name: dict[str, str]
    reference_field: str | None = None
    alias_target_name: str | None = None


@dataclass(frozen=True)
class NonColorToken:
    field: str
    group: str
    source_name: str
    values_by_mode_name: dict[str, str]


@dataclass(frozen=True)
class LayerReport:
    layer: str
    aliases: int
    multi_mode: int
    palette_like: int
    groups: list[str]
