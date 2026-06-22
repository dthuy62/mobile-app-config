from __future__ import annotations

from .helpers import copy_fixture, read_config, run_cli


def test_missing_config_flavors_auto_init_continues(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    result = run_cli(project, "flavors")
    assert result.returncode == 0, result.stderr
    config = read_config(project)
    assert config["module"] == "app"
    assert "dev" in config["flavors"]
    assert 'create("dev")' in (project / "app" / "build.gradle.kts").read_text()


def test_missing_config_assets_auto_init_then_noops(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")
    result = run_cli(project, "assets")
    assert result.returncode == 0, result.stderr
    assert "assets disabled" in result.stdout
    assert (project / "android-mobile-config.json").exists()


def test_missing_config_network_security_auto_init_then_noops(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")
    result = run_cli(project, "network-security")
    assert result.returncode == 0, result.stderr
    assert "network security disabled" in result.stdout
    assert (project / "android-mobile-config.json").exists()


def test_existing_config_is_not_rewritten_without_force(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_existing_flavors_app")
    result = run_cli(project, "init")
    assert result.returncode == 0, result.stderr
    path = project / "android-mobile-config.json"
    before = path.read_text()
    result = run_cli(project, "init")
    assert result.returncode == 0, result.stderr
    assert path.read_text() == before


def test_init_force_rewrites_config(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_existing_flavors_app")
    path = project / "android-mobile-config.json"
    path.write_text('{"module":"wrong","flavors":{"x":{"appName":"X"}}}\n')
    result = run_cli(project, "init", "--force")
    assert result.returncode == 0, result.stderr
    config = read_config(project)
    assert config["module"] == "app"
    assert "dev" in config["flavors"]


def test_existing_flavors_are_detected(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_existing_flavors_app")
    result = run_cli(project, "init", "--force")
    assert result.returncode == 0, result.stderr
    config = read_config(project)
    assert config["dimension"] == "evironment"
    assert config["flavors"]["dev"]["applicationIdSuffix"] == ".dev"
    assert config["flavors"]["dev"]["buildConfigFields"]["CAREER_OPS_ENVIRONMENT"] == "dev"

