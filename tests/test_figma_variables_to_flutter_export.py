from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "figma-variables-to-flutter-export" / "scripts" / "figma-variables-to-flutter-export"
SCRIPT_ROOT = SCRIPT.parent
sys.path.insert(0, str(SCRIPT_ROOT))

from figma_variables_to_flutter_export.models import ExportOptions  # noqa: E402
from figma_variables_to_flutter_export.pipeline import ColorExportPipeline  # noqa: E402


def test_cli_wrapper_imports_package_entrypoint() -> None:
    result = subprocess.run(
        [str(SCRIPT), "--help"],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Export Figma Variables JSON to Flutter Dart files." in result.stdout


def test_color_export_pipeline_renders_from_options(tmp_path: Path) -> None:
    source = tmp_path / "variables.json"
    output = tmp_path / "app_color_base.dart"
    source.write_text(
        json.dumps(
            {
                "Black": {
                    "Black-50": {
                        "$type": "color",
                        "$value": "#E9E9E9",
                    }
                }
            }
        )
    )

    source_text = ColorExportPipeline().run(
        ExportOptions(
            json_file=source,
            output=output,
            layer="base",
            dry_run=True,
        ),
        warn=lambda _message: None,
    )

    assert "abstract final class AppColorBase" in source_text
    assert "static const Color black50 = Color(0xFFE9E9E9);" in source_text


def test_exports_color_tokens_to_dart(tmp_path: Path) -> None:
    source = tmp_path / "variables.json"
    output = tmp_path / "app_colors.dart"
    source.write_text(
        json.dumps(
            {
                "collections": [
                    {
                        "name": "Colors",
                        "modes": [
                            {"modeId": "light", "name": "Light"},
                            {"modeId": "dark", "name": "Dark"},
                        ],
                        "variables": [
                            {
                                "id": "primary",
                                "name": "color/primary",
                                "resolvedType": "COLOR",
                                "valuesByMode": {
                                    "light": {"r": 37 / 255, "g": 99 / 255, "b": 235 / 255, "a": 1},
                                    "dark": {"r": 59 / 255, "g": 130 / 255, "b": 246 / 255, "a": 1},
                                },
                            },
                            {
                                "id": "success",
                                "name": "color/semantic/success",
                                "resolvedType": "COLOR",
                                "valuesByMode": {
                                    "light": "#16A34A",
                                    "dark": "#22C55E",
                                },
                            },
                        ],
                    }
                ]
            }
        )
    )

    result = subprocess.run(
        [
            str(SCRIPT),
            str(source),
            "--type",
            "colors",
            "--layer",
            "system",
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    dart = output.read_text()
    assert "abstract final class AppColors" in dart
    assert "static const Color colorPrimary = Color(0xFF2563EB);" in dart
    assert "abstract final class AppColorsDark" in dart
    assert "static const Color colorSemanticSuccess = Color(0xFF22C55E);" in dart
    assert "class AppColorsTheme extends ThemeExtension<AppColorsTheme>" in dart
    assert "final Color colorSemanticSuccess;" in dart
    assert "final Color colorPrimary;" in dart


def test_exports_nested_design_tokens_with_path_based_names(tmp_path: Path) -> None:
    source = tmp_path / "variables.json"
    output = tmp_path / "app_colors.dart"
    source.write_text(
        json.dumps(
            {
                "Text color": {
                    "Primary": {
                        "$type": "color",
                        "$value": {
                            "colorSpace": "srgb",
                            "components": [0.1019607857, 0.1411764771, 0.2196078449],
                            "alpha": 1,
                            "hex": "#1A2438",
                        },
                    }
                },
                "Overlay bgr": {
                    "Overlay bgr 16": {
                        "$type": "color",
                        "$value": {
                            "colorSpace": "srgb",
                            "components": [0.1176470593, 0.1176470593, 0.1176470593],
                            "alpha": 0.16,
                            "hex": "#1E1E1E",
                        },
                    }
                },
            }
        )
    )

    result = subprocess.run(
        [
            str(SCRIPT),
            str(source),
            "--type",
            "colors",
            "--layer",
            "system",
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    dart = output.read_text()
    assert "static const Color textColorPrimary = Color(0xFF1A2438);" in dart
    assert "static const Color overlayBgr16 = Color(0x291E1E1E);" in dart
    assert "overlayBgrOverlayBgr16" not in dart


def test_exports_palette_tokens_without_repeating_group_prefix(tmp_path: Path) -> None:
    source = tmp_path / "variables.json"
    output = tmp_path / "app_colors.dart"
    source.write_text(
        json.dumps(
            {
                "Black": {
                    "Black-50": {
                        "$type": "color",
                        "$value": {
                            "colorSpace": "srgb",
                            "components": [0.9137254953, 0.9137254953, 0.9137254953],
                            "alpha": 1,
                            "hex": "#E9E9E9",
                        },
                    },
                    "Black-500-16": {
                        "$type": "color",
                        "$value": {
                            "colorSpace": "srgb",
                            "components": [0.1176470593, 0.1176470593, 0.1176470593],
                            "alpha": 0.16,
                            "hex": "#1E1E1E",
                        },
                    },
                }
            }
        )
    )

    result = subprocess.run(
        [
            str(SCRIPT),
            str(source),
            "--type",
            "colors",
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    dart = output.read_text()
    assert "  // Black\n  static const Color black50 = Color(0xFFE9E9E9);" in dart
    assert "static const Color black50016 = Color(0x291E1E1E);" in dart
    assert "blackBlack50" not in dart


def test_system_tokens_reference_base_aliases(tmp_path: Path) -> None:
    source = tmp_path / "variables.json"
    output = tmp_path / "app_colors.dart"
    source.write_text(
        json.dumps(
            {
                "Background": {
                    "Background": {
                        "$type": "color",
                        "$value": {"hex": "#F2F6F9", "alpha": 1},
                        "$extensions": {
                            "com.figma.aliasData": {
                                "targetVariableName": "White/White-bgr",
                            }
                        },
                    }
                },
                "Overlay bgr": {
                    "Overlay bgr 16": {
                        "$type": "color",
                        "$value": {"hex": "#1E1E1E", "alpha": 0.16},
                        "$extensions": {
                            "com.figma.aliasData": {
                                "targetVariableName": "Black/Black-500-16",
                            }
                        },
                    }
                },
            }
        )
    )

    result = subprocess.run(
        [
            str(SCRIPT),
            str(source),
            "--type",
            "colors",
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    dart = output.read_text()
    assert "import 'app_color_base.dart';" in dart
    assert "abstract final class AppColors" in dart
    assert "static const Color background = AppColorBase.whiteBgr;" in dart
    assert "static const Color overlayBgr16 = AppColorBase.black50016;" in dart
    assert "class AppColorsTheme extends ThemeExtension<AppColorsTheme>" in dart


def test_system_tokens_validate_aliases_against_base_json(tmp_path: Path) -> None:
    base = tmp_path / "base.json"
    source = tmp_path / "system.json"
    output = tmp_path / "app_colors.dart"
    base.write_text(
        json.dumps(
            {
                "White": {
                    "White-bgr": {
                        "$type": "color",
                        "$value": {"hex": "#F2F6F9", "alpha": 1},
                    }
                }
            }
        )
    )
    source.write_text(
        json.dumps(
            {
                "Background": {
                    "Background": {
                        "$type": "color",
                        "$value": {"hex": "#F2F6F9", "alpha": 1},
                        "$extensions": {
                            "com.figma.aliasData": {
                                "targetVariableName": "White/White-bgr",
                            }
                        },
                    }
                }
            }
        )
    )

    result = subprocess.run(
        [
            str(SCRIPT),
            str(source),
            "--type",
            "colors",
            "--base-json",
            str(base),
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "static const Color background = AppColorBase.whiteBgr;" in output.read_text()


def test_missing_base_alias_fails_in_strict_mode(tmp_path: Path) -> None:
    base = tmp_path / "base.json"
    source = tmp_path / "system.json"
    output = tmp_path / "app_colors.dart"
    base.write_text(json.dumps({"Black": {"Black-50": {"$type": "color", "$value": "#000000"}}}))
    source.write_text(
        json.dumps(
            {
                "Background": {
                    "Background": {
                        "$type": "color",
                        "$value": {"hex": "#F2F6F9", "alpha": 1},
                        "$extensions": {
                            "com.figma.aliasData": {
                                "targetVariableName": "White/White-bgr",
                            }
                        },
                    }
                }
            }
        )
    )

    result = subprocess.run(
        [
            str(SCRIPT),
            str(source),
            "--base-json",
            str(base),
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Alias target not found in base JSON" in result.stderr


def test_missing_base_alias_falls_back_without_strict(tmp_path: Path) -> None:
    base = tmp_path / "base.json"
    source = tmp_path / "system.json"
    output = tmp_path / "app_colors.dart"
    base.write_text(json.dumps({"Black": {"Black-50": {"$type": "color", "$value": "#000000"}}}))
    source.write_text(
        json.dumps(
            {
                "Background": {
                    "Background": {
                        "$type": "color",
                        "$value": {"hex": "#F2F6F9", "alpha": 1},
                        "$extensions": {
                            "com.figma.aliasData": {
                                "targetVariableName": "White/White-bgr",
                            }
                        },
                    }
                }
            }
        )
    )

    result = subprocess.run(
        [
            str(SCRIPT),
            str(source),
            "--base-json",
            str(base),
            "--no-strict",
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "warning: Alias target not found in base JSON" in result.stderr
    assert "static const Color background = Color(0xFFF2F6F9);" in output.read_text()


def test_ambiguous_auto_layer_fails_in_strict_mode(tmp_path: Path) -> None:
    source = tmp_path / "variables.json"
    output = tmp_path / "app_colors.dart"
    source.write_text(
        json.dumps(
            {
                "Background": {
                    "Primary": {
                        "$type": "color",
                        "$value": {"hex": "#FFFFFF", "alpha": 1},
                    }
                }
            }
        )
    )

    result = subprocess.run(
        [
            str(SCRIPT),
            str(source),
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Cannot confidently detect token layer" in result.stderr


def test_duplicate_fields_fail_with_source_paths(tmp_path: Path) -> None:
    source = tmp_path / "variables.json"
    output = tmp_path / "app_colors.dart"
    source.write_text(
        json.dumps(
            {
                "Black": {
                    "Black-50": {"$type": "color", "$value": "#000000"},
                    "Black 50": {"$type": "color", "$value": "#111111"},
                }
            }
        )
    )

    result = subprocess.run(
        [
            str(SCRIPT),
            str(source),
            "--layer",
            "base",
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Duplicate Dart field names detected" in result.stderr
    assert "Black/Black-50" in result.stderr
    assert "Black/Black 50" in result.stderr
