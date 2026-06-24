from __future__ import annotations

from .helpers import copy_fixture, read_config, run_cli


def test_missing_config_flavors_infers_defaults_without_config_file(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    result = run_cli(project, "flavors")
    assert result.returncode == 0, result.stderr
    assert 'create("dev")' in (project / "app" / "build.gradle.kts").read_text()
    assert (project / "app" / "src" / "dev" / "res" / "values" / "strings.xml").exists()
    assert not (project / "android-app-config.json").exists()


def test_missing_config_assets_noop_does_not_create_config(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")
    result = run_cli(project, "assets")
    assert result.returncode == 0, result.stderr
    assert "assets disabled" in result.stdout
    assert not (project / "android-app-config.json").exists()


def test_missing_config_network_security_noop_does_not_create_config(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")
    result = run_cli(project, "network-security")
    assert result.returncode == 0, result.stderr
    assert "network security disabled" in result.stdout
    assert not (project / "android-app-config.json").exists()


def test_assets_with_options_creates_config(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")
    image = project / "icon.png"
    image.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4"
        b"\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05"
        b"\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    result = run_cli(project, "assets", "--image", "icon.png")
    assert result.returncode == 2
    assert (project / "android-app-config.json").exists()


def test_existing_config_is_not_rewritten_without_force(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_existing_flavors_app")
    result = run_cli(project, "init")
    assert result.returncode == 0, result.stderr
    path = project / "android-app-config.json"
    before = path.read_text()
    result = run_cli(project, "init")
    assert result.returncode == 0, result.stderr
    assert path.read_text() == before


def test_init_force_rewrites_config(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_existing_flavors_app")
    path = project / "android-app-config.json"
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
    # Compatibility: preserve the project's legacy typo instead of rewriting Gradle.
    assert config["dimension"] == "evironment"
    assert config["flavors"]["dev"]["applicationIdSuffix"] == ".dev"
    assert config["flavors"]["dev"]["buildConfigFields"]["CAREER_OPS_ENVIRONMENT"] == "dev"
