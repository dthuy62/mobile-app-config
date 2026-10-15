from __future__ import annotations

import sys

from .helpers import ROOT, copy_fixture, read_config, run_cli

sys.path.insert(0, str(ROOT / "skills" / "android" / "scripts"))

from android_mobile_config.config import DEFAULT_CONFIG, normalize_config  # noqa: E402


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


def test_default_config_uses_neutral_dev_stg_prod() -> None:
    import json

    from android_mobile_config.config import DEFAULT_CONFIG

    text = json.dumps(DEFAULT_CONFIG)
    assert "CAREER_OPS" not in text
    assert "Career Ops" not in text
    flavors = DEFAULT_CONFIG["flavors"]
    assert list(flavors) == ["dev", "stg", "prod"]
    assert flavors["dev"] == {
        "applicationIdSuffix": ".dev",
        "appName": "[DEV] My App",
        "buildConfigFields": {"APP_ENVIRONMENT": "dev", "APP_BASE_URL": "http://10.0.2.2:3000"},
    }
    assert flavors["stg"] == {
        "applicationIdSuffix": ".stg",
        "appName": "[STG] My App",
        "buildConfigFields": {"APP_ENVIRONMENT": "stg", "APP_BASE_URL": ""},
    }
    assert flavors["prod"] == {
        "applicationIdSuffix": "",
        "appName": "My App",
        "buildConfigFields": {"APP_ENVIRONMENT": "prod", "APP_BASE_URL": ""},
    }
    assert list(DEFAULT_CONFIG["firebase"]["flavors"]) == ["dev", "stg", "prod"]


def test_flavor_app_name_rule() -> None:
    from android_mobile_config.config import flavor_app_name

    assert flavor_app_name("dev", "Demo") == "[DEV] Demo"
    assert flavor_app_name("stg", "Demo") == "[STG] Demo"
    assert flavor_app_name("prod", "Demo") == "Demo"
    assert flavor_app_name("staging", "Demo") == "[STAGING] Demo"


def test_init_without_flavors_names_all_default_flavors_from_app_name(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    assert run_cli(project, "init").returncode == 0
    flavors = read_config(project)["flavors"]
    assert [flavors[name]["appName"] for name in flavors] == ["[DEV] No Flavors", "[STG] No Flavors", "No Flavors"]


def test_existing_config_keeps_its_flavors(tmp_path) -> None:
    import json

    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    (project / "android-app-config.json").write_text(
        json.dumps({"flavors": {"dev": {"applicationIdSuffix": ".dev"}, "prod": {"applicationIdSuffix": ""}}})
    )
    assert run_cli(project, "flavors").returncode == 0
    gradle = (project / "app" / "build.gradle.kts").read_text()
    assert 'create("stg")' not in gradle
    assert not (project / "app" / "src" / "stg").exists()


def test_init_on_project_with_flavors_does_not_inject_default_build_config_fields(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_existing_flavors_app")
    result = run_cli(project, "init")
    assert result.returncode == 0, result.stderr
    fields = read_config(project)["flavors"]["dev"]["buildConfigFields"]
    assert "APP_ENVIRONMENT" not in fields
    assert "APP_BASE_URL" not in fields
    assert any(key.startswith("CAREER_OPS_") for key in fields)

    result = run_cli(project, "flavors")
    assert result.returncode == 0, result.stderr
    assert "APP_BASE_URL" not in (project / "app" / "build.gradle.kts").read_text()
    result = run_cli(project, "validate-flavors")
    assert result.returncode == 0, result.stdout + result.stderr


def test_config_flavor_without_fields_gets_flavor_defaults() -> None:
    config = normalize_config({"flavors": {"dev": {}}})
    assert list(config["flavors"]) == ["dev"]
    assert config["flavors"]["dev"] == DEFAULT_CONFIG["flavors"]["dev"]


def test_config_explicit_build_config_fields_are_not_merged_with_defaults() -> None:
    config = normalize_config(
        {
            "flavors": {
                "qa": {"applicationIdSuffix": ".qa", "buildConfigFields": {"X": "1"}},
                "dev": {"buildConfigFields": {}},
            }
        }
    )
    assert list(config["flavors"]) == ["qa", "dev"]
    assert config["flavors"]["qa"]["buildConfigFields"] == {"X": "1"}
    assert config["flavors"]["dev"]["buildConfigFields"] == {}
    assert config["flavors"]["dev"]["applicationIdSuffix"] == ".dev"
