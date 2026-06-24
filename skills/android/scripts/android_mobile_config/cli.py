from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .assets import apply_assets_args, generate_assets, validate_assets
from .config import ConfigError, config_path, load_or_infer, load_or_init, write_config
from .firebase import apply_firebase_args, configure_firebase, validate_firebase
from .gradle_kts import configure_flavors, expected_tasks, validate_flavors
from .network_security import configure_network_security, validate_network_security
from .package_name import configure_package_name, validate_package_name


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "init":
            config, created = load_or_init(root, force=args.force)
            print(f"{'Wrote' if created else 'Using existing'} {config_path(root)}")
            print(f"module={config['module']} dimension={config['dimension']} flavors={','.join(config['flavors'])}")
            return 0

        config = load_or_infer(root)

        if args.command == "flavors":
            tasks = configure_flavors(root, config)
            print("Configured flavors")
            print("Expected tasks: " + ", ".join(tasks))
            return 0
        if args.command == "validate-flavors":
            return report_errors(validate_flavors(root, config), "flavors valid")
        if args.command == "assets":
            if apply_assets_args(config, args):
                write_config(config_path(root), config)
            print(generate_assets(root, config))
            return 0
        if args.command == "validate-assets":
            if getattr(args, "type", None):
                config.setdefault("assets", {})["types"] = asset_types(args.type)
            return report_errors(validate_assets(root, config), "assets valid")
        if args.command == "package-name":
            print(configure_package_name(root, config, args.application_id, args.app_name, args.root_project_name))
            return 0
        if args.command == "validate-package-name":
            return report_errors(validate_package_name(root, config), "package name valid")
        if args.command == "network-security":
            print(configure_network_security(root, config))
            return 0
        if args.command == "validate-network-security":
            return report_errors(validate_network_security(root, config), "network security valid")
        if args.command == "firebase":
            apply_firebase_args(config, args)
            if any([args.mode, args.project, args.flavor, args.create_apps]):
                write_config(config_path(root), config)
            print(configure_firebase(root, config))
            return 0
        if args.command == "validate-firebase":
            return report_errors(validate_firebase(root, config), "firebase valid")
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=Path(sys.argv[0]).name)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Android project root")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--force", action="store_true")
    sub.add_parser("flavors")
    sub.add_parser("validate-flavors")
    assets = sub.add_parser("assets")
    add_asset_args(assets)
    validate_assets_parser = sub.add_parser("validate-assets")
    validate_assets_parser.add_argument("--type", choices=["app-icons", "splash-screens", "all"])
    package_name = sub.add_parser("package-name")
    package_name.add_argument("--application-id", required=True)
    package_name.add_argument("--app-name")
    package_name.add_argument("--root-project-name")
    sub.add_parser("validate-package-name")
    firebase = sub.add_parser(
        "firebase",
        epilog=(
            "examples:\n"
            "  mobile-app-config firebase --mode single --project my-firebase\n"
            "  mobile-app-config firebase --mode per-flavor --flavor dev=my-dev --flavor prod=my-prod\n"
            "  mobile-app-config firebase --mode single --project my-firebase --create-apps"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    firebase.add_argument("--mode", choices=["single", "per-flavor"])
    firebase.add_argument("--project")
    firebase.add_argument("--flavor", action="append", default=[], help="Flavor project mapping: flavor=project")
    firebase.add_argument("--create-apps", action="store_true")
    sub.add_parser("network-security")
    sub.add_parser("validate-network-security")
    sub.add_parser("validate-firebase")
    return parser


def add_asset_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--type", choices=["app-icons", "splash-screens", "all"])
    parser.add_argument("--image")
    parser.add_argument("--background-color")
    parser.add_argument("--dark-image")
    parser.add_argument("--dark-background-color")
    parser.add_argument("--monochrome-image")


def asset_types(value: str) -> list[str]:
    return ["app-icons", "splash-screens"] if value == "all" else [value]


def report_errors(errors: list[str], ok_message: str) -> int:
    if not errors:
        print(ok_message)
        return 0
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
