from __future__ import annotations

import re
from dataclasses import replace
from typing import Any

from .models import ColorToken, LayerReport, Variable, Warn


class ColorTokenBuilder:
    def build(
        self,
        variables: list[Variable],
        *,
        strict: bool,
        base_index: dict[str, str] | None,
        warn: Warn,
    ) -> list[ColorToken]:
        by_id = {var.id: var for var in variables}
        field_sources: dict[str, list[str]] = {}
        tokens: list[ColorToken] = []

        for var in variables:
            if var.resolved_type.upper() != "COLOR":
                continue
            token = self._build_one(var, by_id, base_index, strict, warn)
            field_sources.setdefault(token.field, []).append(token.source_name)
            tokens.append(token)

        return validate_duplicate_fields(tokens, field_sources, strict=strict, warn=warn)

    def _build_one(
        self,
        var: Variable,
        by_id: dict[str, Variable],
        base_index: dict[str, str] | None,
        strict: bool,
        warn: Warn,
    ) -> ColorToken:
        values: dict[str, str] = {}
        for mode_id, raw_value in var.values_by_mode.items():
            mode_name = normalize_mode_name(var.modes.get(str(mode_id), str(mode_id)))
            values[mode_name] = resolve_color(raw_value, by_id, seen={var.id})

        return ColorToken(
            field=dart_field_name(var.name),
            group=token_group_name(var.name),
            source_name=var.name,
            values_by_mode_name=values,
            reference_field=resolve_reference_field(var, base_index, strict, warn),
            alias_target_name=var.alias_target_name,
        )


class LayerClassifier:
    def detect(self, tokens: list[ColorToken], requested: str, *, strict: bool, warn: Warn) -> LayerReport:
        report = build_layer_report(tokens)
        if requested != "auto":
            return replace(report, layer=requested)
        if report.aliases or report.multi_mode:
            return replace(report, layer="system")
        if report.palette_like / len(tokens) >= 0.8:
            return replace(report, layer="base")

        message = (
            "Cannot confidently detect token layer. "
            "Use --layer base or --layer system. "
            f"signals: aliases={report.aliases}, multiMode={report.multi_mode}, "
            f"paletteLike={report.palette_like}/{len(tokens)}, groups={', '.join(report.groups)}"
        )
        if strict:
            raise ValueError(message)
        warn(f"{message}; defaulting to base.")
        return replace(report, layer="base")


def build_base_index(variables: list[Variable], warn: Warn) -> dict[str, str]:
    tokens = ColorTokenBuilder().build(variables, strict=True, base_index=None, warn=warn)
    return {token.source_name: token.field for token in tokens}


def resolve_reference_field(
    var: Variable,
    base_index: dict[str, str] | None,
    strict: bool,
    warn: Warn,
) -> str | None:
    if not var.alias_target_name:
        return None
    if base_index is None:
        return dart_field_name(var.alias_target_name)

    reference_field = base_index.get(var.alias_target_name)
    if reference_field is not None:
        return reference_field

    message = f"Alias target not found in base JSON: {var.name} -> {var.alias_target_name}"
    if strict:
        raise ValueError(message)
    warn(f"{message}; using literal color fallback.")
    return None


def validate_duplicate_fields(
    tokens: list[ColorToken],
    field_sources: dict[str, list[str]],
    *,
    strict: bool,
    warn: Warn,
) -> list[ColorToken]:
    duplicate_messages = [
        f"{field}: {', '.join(sources)}"
        for field, sources in field_sources.items()
        if len(sources) > 1
    ]
    if not duplicate_messages:
        return tokens

    message = "Duplicate Dart field names detected: " + "; ".join(duplicate_messages)
    if strict:
        raise ValueError(message)
    warn(message)
    return suffix_duplicate_fields(tokens)


def suffix_duplicate_fields(tokens: list[ColorToken]) -> list[ColorToken]:
    counts: dict[str, int] = {}
    result: list[ColorToken] = []
    for token in tokens:
        counts[token.field] = counts.get(token.field, 0) + 1
        field = token.field if counts[token.field] == 1 else f"{token.field}{counts[token.field]}"
        result.append(replace(token, field=field))
    return result


def build_layer_report(tokens: list[ColorToken]) -> LayerReport:
    groups = list(dict.fromkeys(token.group for token in tokens))
    aliases = sum(1 for token in tokens if token.alias_target_name)
    multi_mode = sum(1 for token in tokens if len(token.values_by_mode_name) > 1)
    palette_like = sum(1 for token in tokens if is_palette_like(token.source_name))
    return LayerReport("auto", aliases, multi_mode, palette_like, groups)


def is_palette_like(name: str) -> bool:
    parts = name.split("/")
    if len(parts) < 2:
        return False
    first = normalize_word(parts[0])
    second = normalize_word(parts[1])
    return bool(first and second.startswith(first) and re.search(r"\d", parts[1]))


def resolve_color(value: Any, by_id: dict[str, Variable], seen: set[str]) -> str:
    if isinstance(value, dict) and value.get("type") == "VARIABLE_ALIAS":
        alias_id = str(value.get("id"))
        if alias_id in seen:
            raise ValueError(f"Alias cycle detected at {alias_id}.")
        target = by_id.get(alias_id)
        if target is None:
            raise ValueError(f"Alias target not found: {alias_id}.")
        if not target.values_by_mode:
            raise ValueError(f"Alias target has no values: {target.name}.")
        next_value = next(iter(target.values_by_mode.values()))
        return resolve_color(next_value, by_id, seen | {alias_id})

    if isinstance(value, dict):
        if "hex" in value:
            return hex_to_dart_color(str(value["hex"]), value.get("alpha"))
        if isinstance(value.get("components"), list) and len(value["components"]) >= 3:
            return rgba_to_dart_color(value["components"], value.get("alpha", value.get("a", 1)))
        color = value.get("color") if isinstance(value.get("color"), dict) else value
        if all(channel in color for channel in ("r", "g", "b")):
            return rgba_to_dart_color([color["r"], color["g"], color["b"]], color.get("a", color.get("alpha", 1)))

    if isinstance(value, str):
        return hex_to_dart_color(value)

    raise ValueError(f"Unsupported color value: {value!r}")


def rgba_to_dart_color(components: list[Any], alpha: Any) -> str:
    r = to_byte(components[0])
    g = to_byte(components[1])
    b = to_byte(components[2])
    a = to_byte(alpha)
    return f"Color(0x{a:02X}{r:02X}{g:02X}{b:02X})"


def hex_to_dart_color(value: str, alpha: Any = None) -> str:
    hex_value = value.strip().lstrip("#")
    if re.fullmatch(r"[0-9a-fA-F]{6}", hex_value):
        a = to_byte(1 if alpha is None else alpha)
        return f"Color(0x{a:02X}{hex_value.upper()})"
    if re.fullmatch(r"[0-9a-fA-F]{8}", hex_value):
        return f"Color(0x{hex_value.upper()})"
    raise ValueError(f"Unsupported hex color value: {value!r}")


def to_byte(value: Any) -> int:
    number = float(value)
    if 0 <= number <= 1:
        number *= 255
    return max(0, min(255, round(number)))


def normalize_mode_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def dart_field_name(name: str) -> str:
    useful = token_name_words(name)
    first, *rest = useful
    value = first[:1].lower() + first[1:]
    value += "".join(part[:1].upper() + part[1:] for part in rest)
    value = re.sub(r"[^A-Za-z0-9_]", "", value)
    if not value or value[0].isdigit():
        value = f"token{value[:1].upper()}{value[1:]}"
    return value


def token_group_name(name: str) -> str:
    first = name.split("/", 1)[0].strip()
    return first or "Tokens"


def token_name_words(name: str) -> list[str]:
    words: list[str] = []
    for segment in name.split("/"):
        segment_words = [part for part in re.split(r"[^A-Za-z0-9]+", segment) if part]
        if not segment_words:
            continue
        repeated = repeated_prefix_length(words, segment_words)
        words.extend(segment_words[repeated:])
    return words or ["token"]


def repeated_prefix_length(existing: list[str], incoming: list[str]) -> int:
    existing_norm = [normalize_word(word) for word in existing]
    incoming_norm = [normalize_word(word) for word in incoming]
    max_size = min(len(existing_norm), len(incoming_norm))
    for size in range(max_size, 0, -1):
        if existing_norm[-size:] == incoming_norm[:size]:
            return size
    return 0


def normalize_word(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())

