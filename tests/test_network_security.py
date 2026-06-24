from __future__ import annotations

import json

from .helpers import copy_fixture, run_cli


def test_network_security_disabled_makes_no_android_changes(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")
    result = run_cli(project, "init")
    assert result.returncode == 0, result.stderr
    before = sorted(p.relative_to(project).as_posix() for p in (project / "app").rglob("*") if p.is_file())
    result = run_cli(project, "network-security")
    assert result.returncode == 0, result.stderr
    after = sorted(p.relative_to(project).as_posix() for p in (project / "app").rglob("*") if p.is_file())
    assert after == before


def test_network_security_enabled_creates_expected_files(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")
    result = run_cli(project, "init")
    assert result.returncode == 0, result.stderr
    config_path = project / "android-app-config.json"
    config = json.loads(config_path.read_text())
    config["networkSecurity"] = {"enabled": True, "targetFlavors": ["dev"]}
    config_path.write_text(json.dumps(config))
    result = run_cli(project, "network-security")
    assert result.returncode == 0, result.stderr
    assert (project / "app" / "src" / "dev" / "res" / "xml" / "network_security_config.xml").exists()
    manifest = project / "app" / "src" / "dev" / "AndroidManifest.xml"
    assert "android:networkSecurityConfig" in manifest.read_text()


def test_prod_cleartext_is_refused_without_explicit_allow(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")
    result = run_cli(project, "init")
    assert result.returncode == 0, result.stderr
    config_path = project / "android-app-config.json"
    config = json.loads(config_path.read_text())
    config["networkSecurity"] = {
        "enabled": True,
        "targetFlavors": ["prod"],
        "cleartextTrafficPermitted": True,
    }
    config_path.write_text(json.dumps(config))
    result = run_cli(project, "network-security")
    assert result.returncode == 2
    assert "Refusing broad cleartext traffic for prod" in result.stderr

