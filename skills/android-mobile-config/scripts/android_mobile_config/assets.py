from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import ConfigError

DENSITIES = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}


def generate_assets(root: Path, config: dict[str, Any]) -> str:
    assets = config.get("assets", {})
    if not assets.get("enabled", False):
        return "assets disabled; no changes made"
    source = assets.get("sourceIcon", "")
    if not source:
        raise ConfigError("assets.sourceIcon is required when assets.enabled=true")
    try:
        from PIL import Image
    except ImportError as exc:
        raise ConfigError('Pillow is required for asset generation. Install with: python3 -m pip install "Pillow>=10"') from exc

    source_path = (root / source).resolve() if not Path(source).is_absolute() else Path(source)
    if not source_path.exists():
        raise ConfigError(f"Missing source icon: {source_path}")
    image = Image.open(source_path).convert("RGBA")
    if image.width < 432 or image.height < 432:
        raise ConfigError("Source icon must be at least 432x432 pixels")

    module = config["module"]
    res_dir = root / module / "src" / "main" / "res"
    if assets.get("generateLauncherIcon", True):
        for folder, size in DENSITIES.items():
            out_dir = res_dir / folder
            out_dir.mkdir(parents=True, exist_ok=True)
            resized = image.resize((size, size))
            resized.save(out_dir / "ic_launcher.png")
            resized.save(out_dir / "ic_launcher_round.png")
    if assets.get("generateAdaptiveIcon", True):
        adaptive_dir = res_dir / "mipmap-anydpi-v26"
        adaptive_dir.mkdir(parents=True, exist_ok=True)
        xml = adaptive_icon_xml()
        (adaptive_dir / "ic_launcher.xml").write_text(xml)
        (adaptive_dir / "ic_launcher_round.xml").write_text(xml)
    if assets.get("generateSplashIcon", True):
        drawable = res_dir / "drawable"
        drawable.mkdir(parents=True, exist_ok=True)
        image.resize((288, 288)).save(drawable / "ic_splash.png")
    if assets.get("generateNotificationIcon", True):
        drawable = res_dir / "drawable"
        drawable.mkdir(parents=True, exist_ok=True)
        image.resize((96, 96)).save(drawable / "ic_notification.png")
    return "assets generated"


def validate_assets(root: Path, config: dict[str, Any]) -> list[str]:
    assets = config.get("assets", {})
    if not assets.get("enabled", False):
        return []
    module = config["module"]
    res_dir = root / module / "src" / "main" / "res"
    errors: list[str] = []
    for folder in DENSITIES:
        if assets.get("generateLauncherIcon", True) and not (res_dir / folder / "ic_launcher.png").exists():
            errors.append(f"Missing {folder}/ic_launcher.png")
    if assets.get("generateAdaptiveIcon", True) and not (res_dir / "mipmap-anydpi-v26" / "ic_launcher.xml").exists():
        errors.append("Missing adaptive launcher XML")
    if assets.get("generateSplashIcon", True) and not (res_dir / "drawable" / "ic_splash.png").exists():
        errors.append("Missing splash icon")
    if assets.get("generateNotificationIcon", True) and not (res_dir / "drawable" / "ic_notification.png").exists():
        errors.append("Missing notification icon")
    return errors


def adaptive_icon_xml() -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <background android:drawable="@drawable/ic_launcher_background" />\n'
        '    <foreground android:drawable="@mipmap/ic_launcher" />\n'
        "</adaptive-icon>\n"
    )

