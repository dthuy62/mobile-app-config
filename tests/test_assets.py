from __future__ import annotations

import json

from .helpers import copy_fixture, run_cli


def test_assets_missing_source_fails_clearly(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")
    result = run_cli(project, "init")
    assert result.returncode == 0, result.stderr
    config_path = project / "android-mobile-config.json"
    config = json.loads(config_path.read_text())
    config["assets"]["enabled"] = True
    config["assets"]["sourceIcon"] = "missing.png"
    config_path.write_text(json.dumps(config))
    result = run_cli(project, "assets")
    assert result.returncode == 2
    assert "Missing source icon" in result.stderr


def test_assets_empty_source_fails_clearly(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")
    result = run_cli(project, "init")
    assert result.returncode == 0, result.stderr
    config_path = project / "android-mobile-config.json"
    config = json.loads(config_path.read_text())
    config["assets"]["enabled"] = True
    config_path.write_text(json.dumps(config))
    result = run_cli(project, "assets")
    assert result.returncode == 2
    assert "assets.sourceIcon is required" in result.stderr

