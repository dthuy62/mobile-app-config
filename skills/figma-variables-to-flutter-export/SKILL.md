---
name: figma-variables-to-flutter-export
description: Export Figma Variables JSON into Flutter Dart theme files. Use when the user says "/figma-variables-to-flutter-export", "figma variables to flutter", or asks to generate app_colors.dart, typography, spacing, radius, shadow, or design-system Dart files from exported Figma variables.
---

# Figma Variables To Flutter Export

Use this skill to convert exported Figma Variables JSON into deterministic Flutter design-system files. This skill owns the export standard and scripts; repository-specific architecture belongs to the user's prompt or a separate repository-skill.

If a repository-skill exists for the current Flutter project, use it before running this skill so output paths and naming match the codebase. If no repository-skill exists, ask the user or prompt must provide the target file path and conventions.

## Quick Start

Use the bundled CLI at `scripts/figma-variables-to-flutter-export`, resolved relative to this `SKILL.md`.

```bash
figma-variables-to-flutter-export file.json \
  --type colors \
  --output lib/core/design_system/app_colors.dart
```

With explicit project conventions:

```bash
figma-variables-to-flutter-export file.json \
  --type colors \
  --output lib/core/design_system/app_colors.dart \
  --class-prefix App \
  --light-mode light \
  --dark-mode dark
```

Then, from the Flutter app root:

```bash
dart format lib/core/design_system/app_colors.dart
flutter analyze
```

## Core Rules

1. Prefer the bundled script over freeform code generation.
2. Do not scan the repository as part of this skill.
3. Use repository-skill or explicit prompt context for path, class names, architecture, and integration details.
4. Generate only requested variable groups.
5. Keep output idempotent: same JSON and options produce the same Dart file.
6. Do not write into handwritten files unless the user or repository-skill explicitly chooses that path.

## Pipeline Architecture

Read the implementation from the CLI inward:

```text
scripts/figma-variables-to-flutter-export
  -> figma_variables_to_flutter_export/cli.py
  -> figma_variables_to_flutter_export/pipeline.py
  -> figma_variables_to_flutter_export/variables.py
  -> figma_variables_to_flutter_export/colors.py
  -> figma_variables_to_flutter_export/dart_renderer.py
```

The pipeline mirrors Style Dictionary's shape without adding Node.js: parse raw JSON, normalize variables into color tokens, classify base/system layer, resolve aliases, validate unsafe output, then render Dart.

## Supported V1 Export

### Colors

The colors exporter auto-detects token layer:

- Base tokens: no Figma alias metadata. Generate constants only.
- System tokens: has Figma alias metadata. Generate constants plus `ThemeExtension`, and reference base constants when alias target names are available.

Base output:

```bash
figma-variables-to-flutter-export color-base.json \
  --type colors \
  --layer base \
  --output lib/core/design_system/app_color_base.dart
```

Produces:

```dart
abstract final class AppColorBase {
  // Black
  static const Color black50 = Color(0xFFE9E9E9);
  static const Color black50016 = Color(0x291E1E1E);
}
```

System output:

```bash
figma-variables-to-flutter-export colors-system.json \
  --type colors \
  --layer system \
  --base-json color-base.json \
  --output lib/core/design_system/app_colors.dart \
  --base-import app_color_base.dart
```

Produces semantic constants that reference base tokens when aliases exist:

```dart
import 'app_color_base.dart';

abstract final class AppColors {
  // Background
  static const Color background = AppColorBase.whiteBgr;
  static const Color overlayBgr16 = AppColorBase.black50016;
}
```

`--base-json` is optional but recommended. When provided, system aliases are validated against the base token file before Dart is generated.

Strict mode is enabled by default:

- Ambiguous `--layer auto` inputs fail and ask for `--layer base` or `--layer system`.
- Missing system alias targets in `--base-json` fail.
- Duplicate generated Dart field names fail with source token paths.

Use `--no-strict` only when you want best-effort output with warnings and literal color fallback.

For system tokens, the colors exporter also generates:

- Static light constants: `abstract final class AppColors`
- Static dark constants when a dark mode exists: `abstract final class AppColorsDark`
- `ThemeExtension`: `AppColorsTheme`
- `BuildContext` accessor: `context.appColors`

Field names are derived from the full variable path, not from Flutter Material role names. For example, `Text color/Primary` becomes `textColorPrimary`, and `Background Sections/Secondary bgr` becomes `backgroundSectionsSecondaryBgr`.

Every color token is included in `ThemeExtension` by default. To exclude exact Material `ColorScheme` role names such as `primary` or `surface` from the extension, pass:

```bash
figma-variables-to-flutter-export file.json \
  --type colors \
  --output lib/core/design_system/app_colors.dart \
  --exclude-material-extension
```

## JSON Contract

Preferred input shape:

```json
{
  "collections": [
    {
      "name": "Colors",
      "modes": [
        {"modeId": "light", "name": "Light"},
        {"modeId": "dark", "name": "Dark"}
      ],
      "variables": [
        {
          "id": "VariableID:1",
          "name": "color/semantic/success",
          "resolvedType": "COLOR",
          "valuesByMode": {
            "light": {"r": 0.1, "g": 0.6, "b": 0.3, "a": 1},
            "dark": {"r": 0.2, "g": 0.8, "b": 0.5, "a": 1}
          }
        }
      ]
    }
  ]
}
```

The script also accepts common Figma Plugin API and REST-shaped exports when collections, variables, modes, and `valuesByMode` can be found.

Aliases are resolved when a value has this shape:

```json
{"type": "VARIABLE_ALIAS", "id": "VariableID:base"}
```

Alias cycles fail the export.

## Repository-Skill Pattern

Strong usage:

```text
Use $repository-skill first. Then use $figma-variables-to-flutter-export with file.json to export colors into core/design_system/app_colors.dart according to this repository's design-system conventions.
```

Standalone usage:

```text
Use $figma-variables-to-flutter-export with file.json. Export colors to lib/core/design_system/app_colors.dart. Use class prefix App, light mode "Light", dark mode "Dark", static constants plus ThemeExtension for non-Material semantic colors.
```

## Future Groups

Typography, spacing, radius, and shadow should follow the same pattern:

- JSON in
- explicit output path
- deterministic Dart out
- no repo scanner
- repository-skill or prompt supplies integration details
