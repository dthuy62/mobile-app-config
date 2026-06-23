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


def test_package_name_updates_divergent_identities(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    gradle = project / "app" / "build.gradle.kts"
    gradle.write_text(
        gradle.read_text()
        .replace('namespace = "com.example.noflavors"', 'namespace = "com.example"')
        .replace('applicationId = "com.example.noflavors"', 'applicationId = "com.aistudio.taskarena.kymzap"')
    )
    activity = project / "app" / "src" / "main" / "kotlin" / "com" / "example" / "ui" / "MainActivity.kt"
    user = project / "app" / "src" / "main" / "kotlin" / "com" / "example" / "data" / "User.kt"
    activity.parent.mkdir(parents=True)
    user.parent.mkdir(parents=True)
    activity.write_text("package com.example.ui\n\nimport com.example.data.User\n")
    user.write_text("package com.example.data\n")

    result = run_cli(project, "package-name", "--application-id", "me.dthuy.careerops")

    assert result.returncode == 0, result.stderr
    assert 'namespace = "me.dthuy.careerops"' in gradle.read_text()
    assert 'applicationId = "me.dthuy.careerops"' in gradle.read_text()
    moved_activity = project / "app" / "src" / "main" / "kotlin" / "me" / "dthuy" / "careerops" / "ui" / "MainActivity.kt"
    moved_user = project / "app" / "src" / "main" / "kotlin" / "me" / "dthuy" / "careerops" / "data" / "User.kt"
    assert moved_activity.exists()
    assert moved_user.exists()
    assert "package me.dthuy.careerops.ui" in moved_activity.read_text()
    assert "import me.dthuy.careerops.data.User" in moved_activity.read_text()
    assert "package me.dthuy.careerops.data" in moved_user.read_text()
    assert read_config(project)["packageName"]["applicationId"] == "me.dthuy.careerops"
    assert run_cli(project, "validate-package-name").returncode == 0

    before = (gradle.read_text(), moved_activity.read_text(), moved_user.read_text(), read_config(project))
    second = run_cli(project, "package-name", "--application-id", "me.dthuy.careerops")

    assert second.returncode == 0, second.stderr
    assert (gradle.read_text(), moved_activity.read_text(), moved_user.read_text(), read_config(project)) == before


def test_package_name_rejects_ambiguous_source_packages_before_writes(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    init = run_cli(project, "init")
    assert init.returncode == 0, init.stderr
    first = project / "app" / "src" / "main" / "kotlin" / "com" / "foo" / "One.kt"
    second = project / "app" / "src" / "main" / "kotlin" / "org" / "bar" / "Two.kt"
    first.parent.mkdir(parents=True)
    second.parent.mkdir(parents=True)
    first.write_text("package com.foo\n")
    second.write_text("package org.bar\n")
    gradle = project / "app" / "build.gradle.kts"
    config = project / "android-mobile-config.json"
    before = (gradle.read_text(), first.read_text(), second.read_text(), config.read_text() if config.exists() else None)

    result = run_cli(project, "package-name", "--application-id", "me.dthuy.careerops")

    assert result.returncode == 2
    assert "Cannot infer source package" in result.stderr
    assert (gradle.read_text(), first.read_text(), second.read_text(), config.read_text() if config.exists() else None) == before


def test_package_name_preflights_gradle_update_before_source_writes(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    gradle = project / "app" / "build.gradle.kts"
    gradle.write_text(
        """
plugins {
  id("com.android.application")
}

defaultConfig {
  applicationId = "com.example.noflavors"
}
""".lstrip()
    )
    source = project / "app" / "src" / "main" / "kotlin" / "com" / "example" / "noflavors" / "MainActivity.kt"
    source.parent.mkdir(parents=True)
    source.write_text("package com.example.noflavors\n")
    before = (gradle.read_text(), source.read_text())

    result = run_cli(project, "package-name", "--application-id", "me.dthuy.careerops")

    assert result.returncode == 2
    assert "Cannot find android block" in result.stderr
    assert source.exists()
    assert (gradle.read_text(), source.read_text()) == before


def test_package_name_uses_common_source_root_when_namespace_does_not_match(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    gradle = project / "app" / "build.gradle.kts"
    gradle.write_text(gradle.read_text().replace('namespace = "com.example.noflavors"', 'namespace = "org.placeholder"'))
    activity = project / "app" / "src" / "main" / "kotlin" / "com" / "example" / "ui" / "MainActivity.kt"
    user = project / "app" / "src" / "main" / "kotlin" / "com" / "example" / "data" / "User.kt"
    activity.parent.mkdir(parents=True)
    user.parent.mkdir(parents=True)
    activity.write_text("package com.example.ui\n\nimport com.example.data.User\n")
    user.write_text("package com.example.data\n")

    result = run_cli(project, "package-name", "--application-id", "me.dthuy.careerops")

    assert result.returncode == 0, result.stderr
    moved_activity = project / "app" / "src" / "main" / "kotlin" / "me" / "dthuy" / "careerops" / "ui" / "MainActivity.kt"
    assert moved_activity.exists()
    assert "package me.dthuy.careerops.ui" in moved_activity.read_text()


def test_validate_package_name_reports_stale_identity_errors(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_no_flavors_app")
    result = run_cli(project, "package-name", "--application-id", "me.dthuy.careerops")
    assert result.returncode == 0, result.stderr
    gradle = project / "app" / "build.gradle.kts"
    gradle.write_text(
        gradle.read_text()
        .replace('namespace = "me.dthuy.careerops"', 'namespace = "com.example.stale"')
        .replace('applicationId = "me.dthuy.careerops"', 'applicationId = "com.example.stale"')
    )
    stale = project / "app" / "src" / "main" / "kotlin" / "me" / "dthuy" / "careerops" / "Stale.kt"
    stale.parent.mkdir(parents=True)
    stale.write_text("package com.example.stale\n")

    validate = run_cli(project, "validate-package-name")

    assert validate.returncode == 1
    assert "applicationId does not match me.dthuy.careerops" in validate.stderr
    assert "namespace does not match me.dthuy.careerops" in validate.stderr
    assert f"Stale package declaration in {stale}" in validate.stderr
