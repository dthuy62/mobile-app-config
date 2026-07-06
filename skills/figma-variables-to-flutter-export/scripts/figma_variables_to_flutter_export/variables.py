from __future__ import annotations

from typing import Any

from .models import Variable


class VariableParser:
    def parse(self, data: Any) -> list[Variable]:
        if not isinstance(data, dict):
            raise ValueError("Input JSON must be an object.")

        variables: list[Variable] = []
        variables.extend(self._parse_collections(data))
        variables.extend(self._parse_rest_meta(data))
        variables.extend(self._parse_direct_variables(data))
        variables.extend(self._parse_design_tokens(data))

        if not variables:
            raise ValueError("No variables found. Expected collections[].variables, meta.variables, or variables[].")
        return variables

    def _parse_collections(self, data: dict[str, Any]) -> list[Variable]:
        variables: list[Variable] = []
        collections = data.get("collections")
        if not isinstance(collections, list):
            return variables

        for collection in collections:
            if not isinstance(collection, dict):
                continue
            modes = parse_modes(collection.get("modes"))
            for raw_var in collection.get("variables", []):
                var = parse_variable(raw_var, modes)
                if var is not None:
                    variables.append(var)
        return variables

    def _parse_rest_meta(self, data: dict[str, Any]) -> list[Variable]:
        variables: list[Variable] = []
        meta = data.get("meta")
        if not isinstance(meta, dict):
            return variables

        rest_variables = meta.get("variables")
        if not isinstance(rest_variables, dict):
            return variables

        mode_by_collection = parse_rest_collection_modes(
            meta.get("variableCollections") or meta.get("variable_collections")
        )
        for raw_var in rest_variables.values():
            if not isinstance(raw_var, dict):
                continue
            modes = mode_by_collection.get(str(raw_var.get("variableCollectionId")), {})
            var = parse_variable(raw_var, modes)
            if var is not None:
                variables.append(var)
        return variables

    def _parse_direct_variables(self, data: dict[str, Any]) -> list[Variable]:
        variables: list[Variable] = []
        direct_variables = data.get("variables")
        if not isinstance(direct_variables, list):
            return variables

        modes = parse_modes(data.get("modes"))
        for raw_var in direct_variables:
            var = parse_variable(raw_var, modes)
            if var is not None:
                variables.append(var)
        return variables

    def _parse_design_tokens(self, data: dict[str, Any]) -> list[Variable]:
        variables: list[Variable] = []

        def walk(node: Any, path: list[str]) -> None:
            if not isinstance(node, dict):
                return
            token_type = node.get("$type")
            if token_type is not None and "$value" in node:
                variables.append(design_token_variable(node, path, token_type))
                return
            for key, value in node.items():
                if str(key).startswith("$"):
                    continue
                walk(value, path + [str(key)])

        walk(data, [])
        return variables


def parse_rest_collection_modes(raw_collections: Any) -> dict[str, dict[str, str]]:
    mode_by_collection: dict[str, dict[str, str]] = {}
    if not isinstance(raw_collections, dict):
        return mode_by_collection

    for collection_id, collection in raw_collections.items():
        if isinstance(collection, dict):
            mode_by_collection[str(collection_id)] = parse_modes(collection.get("modes"))
    return mode_by_collection


def design_token_variable(node: dict[str, Any], path: list[str], token_type: Any) -> Variable:
    extensions = node.get("$extensions")
    variable_id = None
    alias_target_name = None
    scopes: tuple[str, ...] = ()
    if isinstance(extensions, dict):
        variable_id = extensions.get("com.figma.variableId")
        scopes = parse_scopes(extensions.get("com.figma.scopes"))
        alias_data = extensions.get("com.figma.aliasData")
        if isinstance(alias_data, dict):
            alias_target_name = alias_data.get("targetVariableName")

    return Variable(
        id=str(variable_id or "/".join(path)),
        name="/".join(path),
        resolved_type=str(token_type).upper(),
        values_by_mode={"default": node.get("$value")},
        modes={"default": "default"},
        alias_target_name=str(alias_target_name) if alias_target_name else None,
        scopes=scopes,
    )


def parse_modes(raw_modes: Any) -> dict[str, str]:
    modes: dict[str, str] = {}
    if isinstance(raw_modes, list):
        for mode in raw_modes:
            if isinstance(mode, dict):
                mode_id = str(mode.get("modeId") or mode.get("id") or mode.get("name") or "")
                mode_name = str(mode.get("name") or mode_id)
                if mode_id:
                    modes[mode_id] = mode_name
            elif isinstance(mode, (list, tuple)) and len(mode) >= 2:
                modes[str(mode[1])] = str(mode[0])
    elif isinstance(raw_modes, dict):
        for mode_id, mode in raw_modes.items():
            if isinstance(mode, dict):
                modes[str(mode_id)] = str(mode.get("name") or mode_id)
            else:
                modes[str(mode_id)] = str(mode)
    return modes


def parse_variable(raw_var: Any, modes: dict[str, str]) -> Variable | None:
    if isinstance(raw_var, (list, tuple)) and len(raw_var) >= 2:
        return Variable(
            id=str(raw_var[1]),
            name=str(raw_var[0]),
            resolved_type="COLOR",
            values_by_mode={},
            modes=modes,
        )
    if not isinstance(raw_var, dict):
        return None

    values_by_mode = raw_var.get("valuesByMode") or raw_var.get("values_by_mode") or {}
    return Variable(
        id=str(raw_var.get("id") or raw_var.get("key") or raw_var.get("name")),
        name=str(raw_var.get("name") or ""),
        resolved_type=str(raw_var.get("resolvedType") or raw_var.get("resolved_type") or ""),
        values_by_mode=values_by_mode if isinstance(values_by_mode, dict) else {},
        modes=modes,
        scopes=parse_scopes(raw_var.get("scopes") or raw_var.get("variableScopes") or raw_var.get("variable_scopes")),
    )


def parse_scopes(raw_scopes: Any) -> tuple[str, ...]:
    if not isinstance(raw_scopes, list):
        return ()
    return tuple(str(scope) for scope in raw_scopes)
