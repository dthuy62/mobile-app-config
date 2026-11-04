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
    assert packages == ["com.example.noflavors", "com.example.noflavors.dev", "com.example.noflavors.stg"]
    assert 'id("com.google.gms.google-services") version "4.5.0" apply false' in (
        project / "build.gradle.kts"
    ).read_text()
    assert 'id("com.google.gms.google-services")' in (project / "app" / "build.gradle.kts").read_text()


def test_firebase_reads_the_file_contents_the_cli_returns(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    env = firebase_env(tmp_path, sdkconfig="file")

    result = run_cli(project, "firebase", "--mode", "single", "--project", "shared-project", env=env)

    assert result.returncode == 0, result.stderr
    google_services = json.loads((project / "app" / "google-services.json").read_text())
    assert google_services["project_info"]["project_id"] == "shared-project"
    assert "fileContents" not in google_services
    assert package_names(google_services) == [
        "com.example.noflavors",
        "com.example.noflavors.dev",
        "com.example.noflavors.stg",
    ]
    assert run_cli(project, "validate-firebase", env=env).returncode == 0


def test_firebase_per_flavor_reads_the_file_contents_the_cli_returns(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    env = firebase_env(tmp_path, sdkconfig="file")

    result = run_cli(
        project,
        "firebase",
        "--mode",
        "per-flavor",
        "--flavor",
        "dev=dev-project",
        "--flavor",
        "stg=stg-project",
        "--flavor",
        "prod=prod-project",
        env=env,
    )

    assert result.returncode == 0, result.stderr
    google_services = json.loads((project / "app" / "src" / "dev" / "google-services.json").read_text())
    assert google_services["project_info"]["project_id"] == "dev-project"
    assert package_names(google_services) == ["com.example.noflavors.dev"]


def test_firebase_stops_without_writing_when_the_sdk_config_is_unusable(tmp_path) -> None:
    for shape in ("bad-json", "no-project"):
        project = copy_fixture(tmp_path / shape, "kotlin_no_flavors_app")
        env = firebase_env(tmp_path / shape, sdkconfig=shape)

        result = run_cli(project, "firebase", "--mode", "single", "--project", "shared-project", env=env)

        assert result.returncode != 0, shape
        assert "Cannot read Firebase SDK config" in result.stderr, shape
        assert not (project / "app" / "google-services.json").exists(), shape


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
        "stg=stg-project",
        "--flavor",
        "prod=prod-project",
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert "com.example.noflavors.dev" in (
        project / "app" / "src" / "dev" / "google-services.json"
    ).read_text()
    assert "com.example.noflavors.stg" in (
        project / "app" / "src" / "stg" / "google-services.json"
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


def firebase_env(
    tmp_path: Path, *, logged_in: bool = True, missing_apps: bool = False, sdkconfig: str = "inline"
) -> dict[str, str]:
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
            {"appId": "app-com-example-noflavors-stg", "packageName": "com.example.noflavors.stg"},
        ]
    print(json.dumps({"result": apps}))
elif args[:2] == ["apps:create", "ANDROID"]:
    package = args[args.index("--package-name") + 1]
    print(json.dumps({"result": {"appId": "app-" + package.replace(".", "-"), "packageName": package}}))
elif args[:2] == ["apps:sdkconfig", "ANDROID"]:
    package = package_from_app(args[2])
    config = {
        "project_info": {"project_id": args[args.index("--project") + 1]},
        "client": [{"client_info": {"android_client_info": {"package_name": package}}}]
    }
    shape = os.environ.get("FIREBASE_FAKE_SDKCONFIG")
    if shape == "file":
        result = {"fileName": "google-services.json", "fileContents": json.dumps(config)}
    elif shape == "bad-json":
        result = {"fileName": "google-services.json", "fileContents": "not json"}
    elif shape == "no-project":
        result = {"fileName": "google-services.json", "client": []}
    else:
        result = config
    print(json.dumps({"status": "success", "result": result}))
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
    env["FIREBASE_FAKE_SDKCONFIG"] = sdkconfig
    return env


def package_names(google_services: dict) -> list[str]:
    return sorted(
        client["client_info"]["android_client_info"]["package_name"]
        for client in google_services.get("client", [])
    )
