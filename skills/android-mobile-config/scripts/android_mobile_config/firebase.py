from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .config import ConfigError
from .gradle_kts import ensure_google_services_gradle, package_names, validate_google_services_gradle


def configure_firebase(root: Path, config: dict[str, Any]) -> str:
    firebase = config.get("firebase", {})
    if not firebase.get("enabled", False):
        return "firebase disabled; no changes made"
    preflight_firebase()
    targets = firebase_targets(root, config)
    configs = [download_target(target, bool(firebase.get("createApps", False))) for target in targets]
    write_google_services(root, config, configs)
    ensure_google_services_gradle(root, config)
    return "firebase configured"


def validate_firebase(root: Path, config: dict[str, Any]) -> list[str]:
    firebase = config.get("firebase", {})
    if not firebase.get("enabled", False):
        return []
    errors = validate_google_services_gradle(root, config)
    targets = firebase_targets(root, config)
    mode = firebase.get("mode", "single")
    if mode == "single":
        path = root / config["module"] / "google-services.json"
        data = read_google_services(path, errors)
        if data is not None:
            check_packages(data, [target["package"] for target in targets], errors)
        return errors
    for target in targets:
        path = root / config["module"] / "src" / target["flavor"] / "google-services.json"
        data = read_google_services(path, errors)
        if data is not None:
            check_packages(data, [target["package"]], errors)
    return errors


def apply_firebase_args(config: dict[str, Any], args: Any) -> None:
    if not any([args.mode, args.project, args.flavor, args.create_apps]):
        return
    firebase = config.setdefault("firebase", {})
    firebase["enabled"] = True
    if args.mode:
        firebase["mode"] = args.mode
    if args.project:
        firebase["project"] = args.project
    if args.create_apps:
        firebase["createApps"] = True
    if args.flavor:
        flavors = firebase.setdefault("flavors", {})
        for value in args.flavor:
            if "=" not in value:
                raise ConfigError("--flavor must use flavor=project")
            flavor, project = value.split("=", 1)
            if not flavor or not project:
                raise ConfigError("--flavor must use flavor=project")
            flavors.setdefault(flavor, {})["project"] = project
    validate_firebase_config(config)


def validate_firebase_config(config: dict[str, Any]) -> None:
    firebase = config.get("firebase", {})
    mode = firebase.get("mode", "single")
    if mode not in {"single", "per-flavor"}:
        raise ConfigError("firebase.mode must be single or per-flavor")
    if mode == "single" and not firebase.get("project"):
        raise ConfigError("firebase.project is required for mode=single")
    if mode == "per-flavor":
        projects = firebase.get("flavors", {})
        for flavor in config["flavors"]:
            if not projects.get(flavor, {}).get("project"):
                raise ConfigError(f"firebase.flavors.{flavor}.project is required for mode=per-flavor")


def preflight_firebase() -> None:
    if shutil.which("firebase") is None:
        raise ConfigError("firebase CLI not found; install firebase-tools")
    result = run_firebase(["projects:list", "--json"])
    if result.returncode != 0:
        raise ConfigError("Firebase CLI is not logged in. Run: firebase login. Then rerun: android-mobile-config firebase")


def firebase_targets(root: Path, config: dict[str, Any]) -> list[dict[str, str]]:
    firebase = config.get("firebase", {})
    validate_firebase_config(config)
    packages = package_names(root, config)
    if firebase.get("mode", "single") == "single":
        project = firebase["project"]
        return [{"flavor": flavor, "project": project, "package": package} for flavor, package in packages.items()]
    return [
        {
            "flavor": flavor,
            "project": firebase["flavors"][flavor]["project"],
            "package": package,
        }
        for flavor, package in packages.items()
    ]


def download_target(target: dict[str, str], create_apps: bool) -> dict[str, Any]:
    app = find_android_app(target["project"], target["package"])
    if app is None:
        if not create_apps:
            raise ConfigError(
                f"Missing Firebase Android app for package {target['package']} in project {target['project']}"
            )
        app = create_android_app(target["project"], target["package"], f"{target['flavor']} {target['package']}")
    return sdk_config(target["project"], app["appId"])


def find_android_app(project: str, package: str) -> dict[str, Any] | None:
    result = checked_firebase(["apps:list", "ANDROID", "--project", project, "--json"], project)
    apps = unwrap_result(result)
    if isinstance(apps, dict):
        apps = apps.get("apps", [])
    for app in apps if isinstance(apps, list) else []:
        if app.get("packageName") == package or app.get("androidPackageName") == package:
            return app
    return None


def create_android_app(project: str, package: str, display_name: str) -> dict[str, Any]:
    result = checked_firebase(
        [
            "apps:create",
            "ANDROID",
            display_name,
            "--package-name",
            package,
            "--project",
            project,
            "--json",
        ],
        project,
    )
    app = unwrap_result(result)
    if not isinstance(app, dict) or not app.get("appId"):
        raise ConfigError(f"Cannot create Firebase Android app for package {package} in project {project}")
    return app


def sdk_config(project: str, app_id: str) -> dict[str, Any]:
    result = checked_firebase(["apps:sdkconfig", "ANDROID", app_id, "--project", project, "--json"], project)
    config = unwrap_result(result)
    if isinstance(config, str):
        config = json.loads(config)
    if not isinstance(config, dict):
        raise ConfigError(f"Cannot read Firebase SDK config for app {app_id}")
    return config


def checked_firebase(args: list[str], project: str) -> dict[str, Any]:
    result = run_firebase(args)
    if result.returncode != 0:
        raise ConfigError(f"Cannot access Firebase project {project}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ConfigError("Firebase CLI returned invalid JSON") from exc


def run_firebase(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["firebase", *args], text=True, capture_output=True, check=False)


def unwrap_result(data: dict[str, Any]) -> Any:
    return data.get("result", data)


def write_google_services(root: Path, config: dict[str, Any], configs: list[dict[str, Any]]) -> None:
    firebase = config.get("firebase", {})
    module = root / config["module"]
    if firebase.get("mode", "single") == "single":
        write_json(module / "google-services.json", merge_google_services(configs))
        return
    for target, data in zip(firebase_targets(root, config), configs):
        write_json(module / "src" / target["flavor"] / "google-services.json", data)


def merge_google_services(configs: list[dict[str, Any]]) -> dict[str, Any]:
    if not configs:
        raise ConfigError("No Firebase configs downloaded")
    merged = dict(configs[0])
    clients: list[dict[str, Any]] = []
    seen: set[str] = set()
    for data in configs:
        for client in data.get("client", []):
            package = client.get("client_info", {}).get("android_client_info", {}).get("package_name", "")
            if package and package not in seen:
                seen.add(package)
                clients.append(client)
    merged["client"] = clients
    return merged


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n")


def read_google_services(path: Path, errors: list[str]) -> dict[str, Any] | None:
    if not path.exists():
        errors.append(f"Missing {path}")
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        errors.append(f"Invalid JSON in {path}")
        return None


def check_packages(data: dict[str, Any], expected: list[str], errors: list[str]) -> None:
    packages = {
        client.get("client_info", {}).get("android_client_info", {}).get("package_name")
        for client in data.get("client", [])
    }
    for package in expected:
        if package not in packages:
            errors.append(f"Missing package {package} in google-services.json")
