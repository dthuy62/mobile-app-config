from __future__ import annotations

from .helpers import copy_fixture, run_cli


def test_flavor_configuration_is_idempotent(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    first = run_cli(project, "flavors")
    assert first.returncode == 0, first.stderr
    gradle = project / "app" / "build.gradle.kts"
    strings = project / "app" / "src" / "dev" / "res" / "values" / "strings.xml"
    before = (gradle.read_text(), strings.read_text())
    second = run_cli(project, "flavors")
    assert second.returncode == 0, second.stderr
    assert (gradle.read_text(), strings.read_text()) == before


def test_existing_user_defined_flavor_is_preserved(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_existing_flavors_app")
    result = run_cli(project, "flavors")
    assert result.returncode == 0, result.stderr
    text = (project / "app" / "build.gradle.kts").read_text()
    assert 'create("staging")' in text
    assert 'applicationIdSuffix = ".staging"' in text


def test_unrelated_gradle_blocks_are_preserved(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_existing_flavors_app")
    result = run_cli(project, "flavors")
    assert result.returncode == 0, result.stderr
    text = (project / "app" / "build.gradle.kts").read_text()
    assert "signingConfigs" in text
    assert "buildTypes" in text
    assert "dependencies" in text


def test_validate_flavors_detects_missing_resource(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    result = run_cli(project, "flavors")
    assert result.returncode == 0, result.stderr
    (project / "app" / "src" / "dev" / "res" / "values" / "strings.xml").unlink()
    result = run_cli(project, "validate-flavors")
    assert result.returncode == 1
    assert "Missing app_name resource" in result.stderr


def test_validate_flavors_checks_gradle_tasks_when_wrapper_exists(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    gradlew = project / "gradlew"
    gradlew.write_text("#!/bin/sh\nprintf '%s\\n' assembleDevDebug assembleProdDebug\n")
    gradlew.chmod(0o755)
    result = run_cli(project, "flavors")
    assert result.returncode == 0, result.stderr

    result = run_cli(project, "validate-flavors")

    assert result.returncode == 0, result.stderr


def test_validate_flavors_reports_missing_gradle_variant_when_wrapper_exists(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    gradlew = project / "gradlew"
    gradlew.write_text("#!/bin/sh\nprintf '%s\\n' assembleProdDebug\n")
    gradlew.chmod(0o755)
    result = run_cli(project, "flavors")
    assert result.returncode == 0, result.stderr

    result = run_cli(project, "validate-flavors")

    assert result.returncode == 1
    assert "Gradle does not expose task assembleDevDebug" in result.stderr
