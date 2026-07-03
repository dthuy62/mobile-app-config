from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .models import ExportOptions
from .pipeline import ColorExportPipeline


def main() -> int:
    args = parse_args()
    options = ExportOptions(
        json_file=args.json_file,
        output=args.output,
        token_type=args.type,
        layer=args.layer,
        base_json=args.base_json,
        class_prefix=args.class_prefix,
        base_class=args.base_class,
        base_import=args.base_import,
        light_mode=args.light_mode,
        dark_mode=args.dark_mode,
        exclude_material_extension=args.exclude_material_extension,
        strict=args.strict,
        dry_run=args.dry_run,
    )

    try:
        source = ColorExportPipeline().run(options, warn=warn)
        if options.dry_run:
            print(source)
            return 0
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(source)
        print(f"Generated {options.output}")
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Figma Variables JSON to Flutter Dart files.")
    parser.add_argument("json_file", type=Path)
    parser.add_argument("--type", choices=["colors"], default="colors")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--layer", choices=["auto", "base", "system"], default="auto")
    parser.add_argument("--base-json", type=Path)
    parser.add_argument("--class-prefix", default="App")
    parser.add_argument("--base-class", default="AppColorBase")
    parser.add_argument("--base-import", default="app_color_base.dart")
    parser.add_argument("--light-mode", default="light")
    parser.add_argument("--dark-mode", default="dark")
    parser.add_argument(
        "--exclude-material-extension",
        action="store_true",
        help="Exclude exact Material ColorScheme role names from the generated ThemeExtension.",
    )
    parser.add_argument("--no-strict", dest="strict", action="store_false")
    parser.set_defaults(strict=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)

