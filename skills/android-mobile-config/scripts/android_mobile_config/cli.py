from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .assets import generate_assets, validate_assets
from .config import ConfigError, config_path, load_or_init
from .gradle_kts import configure_flavors, expected_tasks, validate_flavors
from .network_security import configure_network_security, validate_network_security


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

        config, created = load_or_init(root)
        if created:
            print(f"Created {config_path(root)} from project defaults")

        if args.command == "flavors":
            tasks = configure_flavors(root, config)
            print("Configured flavors")
            print("Expected tasks: " + ", ".join(tasks))
            return 0
        if args.command == "validate-flavors":
            return report_errors(validate_flavors(root, config), "flavors valid")
        if args.command == "assets":
            print(generate_assets(root, config))
            return 0
        if args.command == "validate-assets":
            return report_errors(validate_assets(root, config), "assets valid")
        if args.command == "network-security":
            print(configure_network_security(root, config))
            return 0
        if args.command == "validate-network-security":
            return report_errors(validate_network_security(root, config), "network security valid")
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="android-mobile-config")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Android project root")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--force", action="store_true")
    sub.add_parser("flavors")
    sub.add_parser("validate-flavors")
    sub.add_parser("assets")
    sub.add_parser("validate-assets")
    sub.add_parser("network-security")
    sub.add_parser("validate-network-security")
    return parser


def report_errors(errors: list[str], ok_message: str) -> int:
    if not errors:
        print(ok_message)
        return 0
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

