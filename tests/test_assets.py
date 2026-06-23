from __future__ import annotations

import json
from pathlib import Path

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


def test_assets_app_icons_generate_modern_outputs(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")
    logo = write_image(project / "branding" / "logo.png")
    mono = write_image(project / "branding" / "mono.png")
    res = project / "app" / "src" / "main" / "res"
    for folder in ["mipmap-mdpi", "mipmap-hdpi", "mipmap-xhdpi", "mipmap-xxhdpi", "mipmap-xxxhdpi"]:
        legacy = res / folder
        legacy.mkdir(parents=True, exist_ok=True)
        (legacy / "ic_launcher.webp").write_bytes(b"legacy")
        (legacy / "ic_launcher_round.webp").write_bytes(b"legacy")
    drawable = res / "drawable"
    drawable.mkdir(parents=True, exist_ok=True)
    (drawable / "ic_launcher_foreground.xml").write_text("<vector />\n")

    result = run_cli(
        project,
        "assets",
        "--type",
        "app-icons",
        "--image",
        str(logo.relative_to(project)),
        "--background-color",
        "#112233",
        "--monochrome-image",
        str(mono.relative_to(project)),
    )

    assert result.returncode == 0, result.stderr
    assert_png_size(res / "mipmap-mdpi" / "ic_launcher.png", (48, 48))
    assert_png_size(res / "mipmap-xxxhdpi" / "ic_launcher_round.png", (192, 192))
    assert_png_size(res / "drawable" / "ic_launcher_foreground.png", (432, 432))
    assert not list(res.glob("mipmap-*/ic_launcher.webp"))
    assert not list(res.glob("mipmap-*/ic_launcher_round.webp"))
    assert not (res / "drawable" / "ic_launcher_foreground.xml").exists()
    assert 'android:color="#112233"' in (res / "drawable" / "ic_launcher_background.xml").read_text()
    adaptive = (res / "mipmap-anydpi-v26" / "ic_launcher.xml").read_text()
    assert "@drawable/ic_launcher_foreground" in adaptive
    assert "@drawable/ic_launcher_background" in adaptive
    assert "@drawable/ic_launcher_monochrome" in adaptive

    before = snapshot_files(res)
    second = run_cli(project, "assets", "--type", "app-icons")
    assert second.returncode == 0, second.stderr
    assert snapshot_files(res) == before


def test_assets_validate_detects_duplicate_launcher_resources(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")
    logo = write_image(project / "branding" / "logo.png")
    result = run_cli(project, "assets", "--type", "app-icons", "--image", str(logo.relative_to(project)))
    assert result.returncode == 0, result.stderr
    res = project / "app" / "src" / "main" / "res"
    (res / "mipmap-mdpi" / "ic_launcher.webp").write_bytes(b"legacy")
    (res / "mipmap-hdpi" / "ic_launcher_round.webp").write_bytes(b"legacy")
    (res / "drawable" / "ic_launcher_foreground.xml").write_text("<vector />\n")

    result = run_cli(project, "validate-assets", "--type", "app-icons")

    assert result.returncode == 1
    assert "Duplicate launcher resource mipmap-mdpi/ic_launcher" in result.stderr
    assert "Duplicate launcher resource mipmap-hdpi/ic_launcher_round" in result.stderr
    assert "Duplicate launcher resource drawable/ic_launcher_foreground" in result.stderr


def test_assets_splash_screens_generate_theme_and_manifest(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")
    manifest = project / "app" / "src" / "main" / "AndroidManifest.xml"
    manifest.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<manifest xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <application android:label="@string/app_name">\n'
        '        <activity android:name=".MainActivity" android:theme="@style/ExistingTheme" android:exported="true">\n'
        '            <intent-filter>\n'
        '                <action android:name="android.intent.action.MAIN" />\n'
        '                <category android:name="android.intent.category.LAUNCHER" />\n'
        '            </intent-filter>\n'
        '        </activity>\n'
        '    </application>\n'
        '</manifest>\n'
    )
    logo = write_image(project / "branding" / "splash.png")
    dark = write_image(project / "branding" / "splash-dark.png")

    result = run_cli(
        project,
        "assets",
        "--type",
        "splash-screens",
        "--image",
        str(logo.relative_to(project)),
        "--background-color",
        "#FFFFFF",
        "--dark-image",
        str(dark.relative_to(project)),
        "--dark-background-color",
        "#000000",
    )

    assert result.returncode == 0, result.stderr
    res = project / "app" / "src" / "main" / "res"
    assert_png_size(res / "drawable" / "ic_splash.png", (288, 288))
    assert (res / "drawable" / "splash_screen.xml").exists()
    assert (res / "values-v31" / "themes.xml").exists()
    assert (res / "drawable-night" / "ic_splash.png").exists()
    assert (res / "values-night-v31" / "themes.xml").exists()
    assert 'android:theme="@style/Theme.App.Starting"' in manifest.read_text()
    themes = (res / "values-v31" / "themes.xml").read_text()
    assert "android:windowSplashScreenBackground" in themes
    assert "android:windowSplashScreenAnimatedIcon" in themes
    assert "postSplashScreenTheme" not in themes
    assert "@style/ExistingTheme" in themes
    assert 'parent="@style/ExistingTheme"' in themes
    legacy_themes = (res / "values" / "themes.xml").read_text()
    assert 'parent="@style/ExistingTheme"' in legacy_themes
    assert "android:windowBackground" in legacy_themes

    before = snapshot_files(res)
    second = run_cli(project, "assets", "--type", "splash-screens")
    assert second.returncode == 0, second.stderr
    assert snapshot_files(res) == before


def test_assets_validate_type_detects_missing_splash_file(tmp_path) -> None:
    project = copy_fixture(tmp_path, "kotlin_basic_app")
    logo = write_image(project / "branding" / "splash.png")
    result = run_cli(project, "assets", "--type", "splash-screens", "--image", str(logo.relative_to(project)))
    assert result.returncode == 0, result.stderr
    (project / "app" / "src" / "main" / "res" / "drawable" / "splash_screen.xml").unlink()

    result = run_cli(project, "validate-assets", "--type", "splash-screens")

    assert result.returncode == 1
    assert "Missing splash_screen.xml" in result.stderr


def write_image(path: Path, *, size: tuple[int, int] = (512, 512)) -> Path:
    from PIL import Image, ImageDraw

    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((96, 96, 416, 416), fill=(20, 120, 220, 255))
    image.save(path)
    return path


def assert_png_size(path: Path, size: tuple[int, int]) -> None:
    from PIL import Image

    with Image.open(path) as image:
        assert image.size == size


def snapshot_files(root: Path) -> dict[str, bytes]:
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()}
