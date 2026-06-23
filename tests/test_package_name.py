from __future__ import annotations

from .helpers import copy_fixture, read_config, run_cli


def test_package_name_updates_gradle_and_sources(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    kotlin = project / "app" / "src" / "main" / "kotlin" / "com" / "example" / "noflavors" / "MainActivity.kt"
    java = project / "app" / "src" / "debug" / "java" / "com" / "example" / "noflavors" / "DebugOnly.java"
    kotlin.parent.mkdir(parents=True)
    java.parent.mkdir(parents=True)
    kotlin.write_text(
        "package com.example.noflavors\n\n"
        "import com.example.noflavors.DebugOnly\n"
        "import android.app.Activity\n"
    )
    java.write_text("package com.example.noflavors;\n\nimport com.example.noflavors.MainActivity;\n")

    result = run_cli(project, "package-name", "--application-id", "com.aistudio.taskarena.kymzap")

    assert result.returncode == 0, result.stderr
    gradle = (project / "app" / "build.gradle.kts").read_text()
    assert 'namespace = "com.aistudio.taskarena.kymzap"' in gradle
    assert 'applicationId = "com.aistudio.taskarena.kymzap"' in gradle
    moved_kotlin = (
        project
        / "app"
        / "src"
        / "main"
        / "kotlin"
        / "com"
        / "aistudio"
        / "taskarena"
        / "kymzap"
        / "MainActivity.kt"
    )
    moved_java = (
        project
        / "app"
        / "src"
        / "debug"
        / "java"
        / "com"
        / "aistudio"
        / "taskarena"
        / "kymzap"
        / "DebugOnly.java"
    )
    assert moved_kotlin.exists()
    assert moved_java.exists()
    assert "package com.aistudio.taskarena.kymzap" in moved_kotlin.read_text()
    assert "import com.aistudio.taskarena.kymzap.DebugOnly" in moved_kotlin.read_text()
    assert "package com.aistudio.taskarena.kymzap;" in moved_java.read_text()
    assert read_config(project)["packageName"]["applicationId"] == "com.aistudio.taskarena.kymzap"


def test_package_name_rejects_invalid_package(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")

    result = run_cli(project, "package-name", "--application-id", "com.1bad.name")

    assert result.returncode == 2
    assert "Invalid applicationId" in result.stderr


def test_package_name_is_idempotent_and_updates_firebase_packages(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")

    first = run_cli(project, "package-name", "--application-id", "com.aistudio.taskarena.kymzap")
    assert first.returncode == 0, first.stderr
    gradle = project / "app" / "build.gradle.kts"
    config = project / "android-mobile-config.json"
    before = (gradle.read_text(), config.read_text())
    second = run_cli(project, "package-name", "--application-id", "com.aistudio.taskarena.kymzap")
    assert second.returncode == 0, second.stderr
    assert (gradle.read_text(), config.read_text()) == before

    firebase = run_cli(project, "firebase")

    assert firebase.returncode == 0
    assert "firebase disabled" in firebase.stdout
    assert run_cli(project, "validate-package-name").returncode == 0
