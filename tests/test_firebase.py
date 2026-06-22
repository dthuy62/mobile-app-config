from __future__ import annotations

import json
import os
from pathlib import Path

from .helpers import copy_fixture, read_config, run_cli


def test_firebase_flags_write_config_and_single_project_files(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    env = firebase_env(tmp_path)

    result = run_cli(project, "firebase", "--mode", "single", "--project", "shared-project", env=env)

    assert result.returncode == 0, result.stderr
    config = read_config(project)
    assert config["firebase"]["enabled"] is True
    assert config["firebase"]["mode"] == "single"
    assert config["firebase"]["project"] == "shared-project"
    google_services = json.loads((project / "app" / "google-services.json").read_text())
    packages = package_names(google_services)
    assert packages == ["com.example.noflavors", "com.example.noflavors.dev"]
    assert 'id("com.google.gms.google-services") version "4.5.0" apply false' in (
        project / "build.gradle.kts"
    ).read_text()
    assert 'id("com.google.gms.google-services")' in (project / "app" / "build.gradle.kts").read_text()


def test_firebase_per_flavor_writes_flavor_files(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    env = firebase_env(tmp_path)

    result = run_cli(
        project,
        "firebase",
        "--mode",
        "per-flavor",
        "--flavor",
        "dev=dev-project",
        "--flavor",
        "prod=prod-project",
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert "com.example.noflavors.dev" in (
        project / "app" / "src" / "dev" / "google-services.json"
    ).read_text()
    assert "com.example.noflavors" in (project / "app" / "src" / "prod" / "google-services.json").read_text()


def test_firebase_missing_login_stops_without_writing_files(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    env = firebase_env(tmp_path, logged_in=False)

    result = run_cli(project, "firebase", "--mode", "single", "--project", "shared-project", env=env)

    assert result.returncode == 2
    assert "firebase login" in result.stderr
    assert not (project / "app" / "google-services.json").exists()


def test_firebase_disabled_noops(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")

    result = run_cli(project, "firebase")

    assert result.returncode == 0, result.stderr
    assert "firebase disabled" in result.stdout
    assert not (project / "app" / "google-services.json").exists()


def test_firebase_missing_cli_fails_clearly(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    env = os.environ.copy()
    env["PATH"] = ""

    result = run_cli(project, "firebase", "--mode", "single", "--project", "shared-project", env=env)

    assert result.returncode == 2
    assert "firebase CLI not found" in result.stderr


def test_firebase_missing_app_requires_create_apps(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    env = firebase_env(tmp_path, missing_apps=True)

    result = run_cli(project, "firebase", "--mode", "single", "--project", "shared-project", env=env)

    assert result.returncode == 2
    assert "Missing Firebase Android app" in result.stderr
    assert "com.example.noflavors.dev" in result.stderr


def test_firebase_create_apps_allows_missing_app(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    env = firebase_env(tmp_path, missing_apps=True)

    result = run_cli(
        project,
        "firebase",
        "--mode",
        "single",
        "--project",
        "shared-project",
        "--create-apps",
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert (project / "app" / "google-services.json").exists()


def test_validate_firebase_detects_package_mismatch(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    env = firebase_env(tmp_path)
    result = run_cli(project, "firebase", "--mode", "single", "--project", "shared-project", env=env)
    assert result.returncode == 0, result.stderr
    path = project / "app" / "google-services.json"
    data = json.loads(path.read_text())
    data["client"] = [
        client
        for client in data["client"]
        if client["client_info"]["android_client_info"]["package_name"] != "com.example.noflavors.dev"
    ]
    path.write_text(json.dumps(data))

    result = run_cli(project, "validate-firebase")

    assert result.returncode == 1
    assert "Missing package com.example.noflavors.dev" in result.stderr


def test_firebase_help_lists_modes_and_flags(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")

    result = run_cli(project, "firebase", "--help")

    assert result.returncode == 0
    assert "--mode" in result.stdout
    assert "--project" in result.stdout
    assert "--create-apps" in result.stdout


def firebase_env(tmp_path: Path, *, logged_in: bool = True, missing_apps: bool = False) -> dict[str, str]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    firebase = bin_dir / "firebase"
    firebase.write_text(
        """#!/usr/bin/env python3
import json
import os
import sys

args = sys.argv[1:]
if os.environ.get("FIREBASE_FAKE_LOGGED_IN") == "0":
    print("Error: not logged in", file=sys.stderr)
    raise SystemExit(1)

def package_from_app(app_id):
    return app_id.split("app-", 1)[1].replace("-", ".")

if args[:2] == ["projects:list", "--json"]:
    print(json.dumps({"result": [{"projectId": "shared-project"}]}))
elif args[:2] == ["apps:list", "ANDROID"]:
    if os.environ.get("FIREBASE_FAKE_MISSING_APPS") == "1":
        apps = []
    else:
        apps = [
            {"appId": "app-com-example-noflavors", "packageName": "com.example.noflavors"},
            {"appId": "app-com-example-noflavors-dev", "packageName": "com.example.noflavors.dev"},
        ]
    print(json.dumps({"result": apps}))
elif args[:2] == ["apps:create", "ANDROID"]:
    package = args[args.index("--package-name") + 1]
    print(json.dumps({"result": {"appId": "app-" + package.replace(".", "-"), "packageName": package}}))
elif args[:2] == ["apps:sdkconfig", "ANDROID"]:
    package = package_from_app(args[2])
    print(json.dumps({"result": {
        "project_info": {"project_id": args[args.index("--project") + 1]},
        "client": [{"client_info": {"android_client_info": {"package_name": package}}}]
    }}))
else:
    print("unexpected firebase args: " + " ".join(args), file=sys.stderr)
    raise SystemExit(64)
"""
    )
    firebase.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    env["FIREBASE_FAKE_LOGGED_IN"] = "1" if logged_in else "0"
    env["FIREBASE_FAKE_MISSING_APPS"] = "1" if missing_apps else "0"
    return env


def package_names(google_services: dict) -> list[str]:
    return sorted(
        client["client_info"]["android_client_info"]["package_name"]
        for client in google_services.get("client", [])
    )
