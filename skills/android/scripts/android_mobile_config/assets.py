from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from .config import ConfigError

ANDROID_NS = "http://schemas.android.com/apk/res/android"
ET.register_namespace("android", ANDROID_NS)

DENSITIES = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}
ASSET_TYPES = {"app-icons", "splash-screens"}


def apply_assets_args(config: dict[str, Any], args: Any) -> bool:
    changed = False
    assets = config.setdefault("assets", {})
    if args.type:
        assets["types"] = ["app-icons", "splash-screens"] if args.type == "all" else [args.type]
        changed = True
    if any([args.image, args.background_color, args.dark_image, args.dark_background_color, args.monochrome_image]):
        assets["enabled"] = True
        changed = True
    types = asset_types(assets)
    if args.image:
        if "app-icons" in types:
            assets.setdefault("appIcons", {})["image"] = args.image
        if "splash-screens" in types:
            assets.setdefault("splashScreens", {})["image"] = args.image
    if args.background_color:
        validate_color(args.background_color)
        if "app-icons" in types:
            assets.setdefault("appIcons", {})["backgroundColor"] = args.background_color
        if "splash-screens" in types:
            assets.setdefault("splashScreens", {})["backgroundColor"] = args.background_color
    if args.dark_image:
        assets.setdefault("splashScreens", {})["darkImage"] = args.dark_image
    if args.dark_background_color:
        validate_color(args.dark_background_color)
        assets.setdefault("splashScreens", {})["darkBackgroundColor"] = args.dark_background_color
    if args.monochrome_image:
        assets.setdefault("appIcons", {})["monochromeImage"] = args.monochrome_image
    return changed


def generate_assets(root: Path, config: dict[str, Any]) -> str:
    assets = config.get("assets", {})
    if not assets.get("enabled", False):
        return "assets disabled; no changes made"
    load_pillow()
    outputs: list[str] = []
    if "app-icons" in asset_types(assets):
        generate_app_icons(root, config)
        outputs.append("app icons")
    if "splash-screens" in asset_types(assets):
        generate_splash_screens(root, config)
        outputs.append("splash screens")
    return "assets generated: " + ", ".join(outputs)


def validate_assets(root: Path, config: dict[str, Any]) -> list[str]:
    assets = config.get("assets", {})
    if not assets.get("enabled", False):
        return []
    errors: list[str] = []
    if "app-icons" in asset_types(assets):
        errors.extend(validate_app_icons(root, config))
    if "splash-screens" in asset_types(assets):
        errors.extend(validate_splash_screens(root, config))
    return errors


def generate_app_icons(root: Path, config: dict[str, Any]) -> None:
    image_config = app_icon_config(config)
    source = image_config.get("image", "") or config.get("assets", {}).get("sourceIcon", "")
    if not source:
        raise ConfigError("assets.sourceIcon is required when assets.enabled=true")
    image = open_image(root, source)
    if image.width < 432 or image.height < 432:
        raise ConfigError("Source icon must be at least 432x432 pixels")
    background = image_config.get("backgroundColor", "#FFFFFF")
    validate_color(background)

    res_dir = resource_dir(root, config)
    for folder, size in DENSITIES.items():
        out_dir = res_dir / folder
        out_dir.mkdir(parents=True, exist_ok=True)
        remove_if_exists(out_dir / "ic_launcher.webp")
        remove_if_exists(out_dir / "ic_launcher_round.webp")
        icon = padded(image, size, 0.78)
        icon.save(out_dir / "ic_launcher.png")
        icon.save(out_dir / "ic_launcher_round.png")

    drawable = res_dir / "drawable"
    drawable.mkdir(parents=True, exist_ok=True)
    remove_if_exists(drawable / "ic_launcher_foreground.xml")
    padded(image, 432, 0.67).save(drawable / "ic_launcher_foreground.png")
    (drawable / "ic_launcher_background.xml").write_text(color_drawable_xml(background))

    mono = image_config.get("monochromeImage", "")
    if mono:
        mono_image = open_image(root, mono)
        padded(mono_image, 432, 0.67).save(drawable / "ic_launcher_monochrome.png")

    adaptive = res_dir / "mipmap-anydpi-v26"
    adaptive.mkdir(parents=True, exist_ok=True)
    xml = adaptive_icon_xml(monochrome=bool(mono))
    (adaptive / "ic_launcher.xml").write_text(xml)
    (adaptive / "ic_launcher_round.xml").write_text(xml)


def generate_splash_screens(root: Path, config: dict[str, Any]) -> None:
    splash = splash_config(config)
    source = splash.get("image", "") or config.get("assets", {}).get("sourceIcon", "")
    if not source:
        raise ConfigError("assets.splashScreens.image is required for splash-screens")
    image = open_image(root, source)
    if image.width < 432 or image.height < 432:
        raise ConfigError("Splash image must be at least 432x432 pixels")
    background = splash.get("backgroundColor", "#FFFFFF")
    validate_color(background)

    res_dir = resource_dir(root, config)
    existing_parent = current_starting_theme_parent(res_dir)
    parent_theme = existing_parent or current_manifest_theme(root, config) or "@style/Theme.App"
    write_splash_variant(res_dir, image, background, parent_theme, night=False)
    dark_image = splash.get("darkImage", "")
    if dark_image or splash.get("darkBackgroundColor"):
        dark = open_image(root, dark_image) if dark_image else image
        dark_background = splash.get("darkBackgroundColor") or "#000000"
        validate_color(dark_background)
        write_splash_variant(res_dir, dark, dark_background, parent_theme, night=True)
    update_manifest_theme(root, config, existing_parent)


def write_splash_variant(res_dir: Path, image: Any, background: str, parent_theme: str, *, night: bool) -> None:
    drawable = res_dir / ("drawable-night" if night else "drawable")
    values = res_dir / ("values-night" if night else "values")
    values_v31 = res_dir / ("values-night-v31" if night else "values-v31")
    drawable.mkdir(parents=True, exist_ok=True)
    values.mkdir(parents=True, exist_ok=True)
    values_v31.mkdir(parents=True, exist_ok=True)
    padded(image, 288, 0.67).save(drawable / "ic_splash.png")
    (drawable / "splash_screen.xml").write_text(splash_layer_xml())
    merge_colors(values / "colors.xml", {"splash_screen_background": background})
    (values / "themes.xml").write_text(legacy_themes_xml(parent_theme))
    (values_v31 / "themes.xml").write_text(v31_themes_xml(parent_theme))


def validate_app_icons(root: Path, config: dict[str, Any]) -> list[str]:
    res_dir = resource_dir(root, config)
    errors: list[str] = []
    for folder in DENSITIES:
        if not (res_dir / folder / "ic_launcher.png").exists():
            errors.append(f"Missing {folder}/ic_launcher.png")
    if not (res_dir / "drawable" / "ic_launcher_foreground.png").exists():
        errors.append("Missing adaptive launcher foreground")
    if not (res_dir / "drawable" / "ic_launcher_background.xml").exists():
        errors.append("Missing adaptive launcher background")
    if not (res_dir / "mipmap-anydpi-v26" / "ic_launcher.xml").exists():
        errors.append("Missing adaptive launcher XML")
    if app_icon_config(config).get("monochromeImage") and not (res_dir / "drawable" / "ic_launcher_monochrome.png").exists():
        errors.append("Missing monochrome launcher icon")
    errors.extend(validate_duplicate_launcher_resources(res_dir))
    return errors


def validate_splash_screens(root: Path, config: dict[str, Any]) -> list[str]:
    res_dir = resource_dir(root, config)
    errors: list[str] = []
    for path, label in [
        (res_dir / "drawable" / "ic_splash.png", "splash icon"),
        (res_dir / "drawable" / "splash_screen.xml", "splash_screen.xml"),
        (res_dir / "values" / "themes.xml", "legacy splash theme"),
        (res_dir / "values-v31" / "themes.xml", "Android 12 splash theme"),
    ]:
        if not path.exists():
            errors.append(f"Missing {label}")
    if has_dark_splash(config):
        for path, label in [
            (res_dir / "drawable-night" / "ic_splash.png", "night splash icon"),
            (res_dir / "drawable-night" / "splash_screen.xml", "night splash_screen.xml"),
            (res_dir / "values-night-v31" / "themes.xml", "night Android 12 splash theme"),
        ]:
            if not path.exists():
                errors.append(f"Missing {label}")
    manifest = manifest_path(root, config)
    if not manifest.exists() or "Theme.App.Starting" not in manifest.read_text():
        errors.append("Missing splash theme in AndroidManifest.xml")
    return errors


def asset_types(assets: dict[str, Any]) -> set[str]:
    raw = assets.get("types") or ["app-icons"]
    return {item for item in raw if item in ASSET_TYPES}


def app_icon_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("assets", {}).setdefault("appIcons", {})


def splash_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("assets", {}).setdefault("splashScreens", {})


def resource_dir(root: Path, config: dict[str, Any]) -> Path:
    return root / config["module"] / "src" / "main" / "res"


def manifest_path(root: Path, config: dict[str, Any]) -> Path:
    return root / config["module"] / "src" / "main" / "AndroidManifest.xml"


def load_pillow() -> None:
    try:
        import PIL  # noqa: F401
    except ImportError as exc:
        raise ConfigError('Pillow is required for asset generation. Install with: python3 -m pip install "Pillow>=10"') from exc


def open_image(root: Path, source: str) -> Any:
    from PIL import Image

    path = (root / source).resolve() if not Path(source).is_absolute() else Path(source)
    if not path.exists():
        raise ConfigError(f"Missing source icon: {path}")
    return Image.open(path).convert("RGBA")


def padded(image: Any, size: int, scale: float) -> Any:
    from PIL import Image

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    limit = max(1, int(size * scale))
    copy = image.copy()
    copy.thumbnail((limit, limit))
    canvas.alpha_composite(copy, ((size - copy.width) // 2, (size - copy.height) // 2))
    return canvas


def validate_color(value: str) -> None:
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
        raise ConfigError(f"Invalid color {value}; expected #RRGGBB")


def color_drawable_xml(color: str) -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">\n'
        f'    <solid android:color="{color}" />\n'
        "</shape>\n"
    )


def adaptive_icon_xml(*, monochrome: bool) -> str:
    extra = '    <monochrome android:drawable="@drawable/ic_launcher_monochrome" />\n' if monochrome else ""
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <background android:drawable="@drawable/ic_launcher_background" />\n'
        '    <foreground android:drawable="@drawable/ic_launcher_foreground" />\n'
        f"{extra}"
        "</adaptive-icon>\n"
    )


def splash_layer_xml() -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<layer-list xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <item android:drawable="@color/splash_screen_background" />\n'
        "    <item>\n"
        '        <bitmap android:gravity="center" android:src="@drawable/ic_splash" />\n'
        "    </item>\n"
        "</layer-list>\n"
    )


def legacy_themes_xml(parent_theme: str) -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<resources>\n"
        '    <style name="Theme.App" parent="@android:style/Theme.Material.Light.NoActionBar" />\n'
        f'    <style name="Theme.App.Starting" parent="{parent_theme}">\n'
        '        <item name="android:windowBackground">@drawable/splash_screen</item>\n'
        "    </style>\n"
        "</resources>\n"
    )


def v31_themes_xml(parent_theme: str) -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<resources>\n"
        f'    <style name="Theme.App.Starting" parent="{parent_theme}">\n'
        '        <item name="android:windowSplashScreenBackground">@color/splash_screen_background</item>\n'
        '        <item name="android:windowSplashScreenAnimatedIcon">@drawable/ic_splash</item>\n'
        "    </style>\n"
        "</resources>\n"
    )


def merge_colors(path: Path, colors: dict[str, str]) -> None:
    if path.exists():
        root = ET.fromstring(path.read_text())
    else:
        root = ET.Element("resources")
    existing = {item.get("name"): item for item in root.findall("color")}
    for name, value in colors.items():
        item = existing.get(name)
        if item is None:
            item = ET.SubElement(root, "color", {"name": name})
        item.text = value
    path.write_text(xml_text(root))


def update_manifest_theme(root: Path, config: dict[str, Any], existing_parent: str | None = None) -> None:
    path = manifest_path(root, config)
    if not path.exists():
        raise ConfigError(f"Missing AndroidManifest.xml: {path}")
    tree = ET.parse(path)
    manifest = tree.getroot()
    application = manifest.find("application")
    if application is None:
        raise ConfigError("AndroidManifest.xml is missing <application>")
    target = find_launcher_activity(application) or application
    current_theme = target.get(f"{{{ANDROID_NS}}}theme")
    old_theme = existing_parent or current_theme or application.get(f"{{{ANDROID_NS}}}theme") or "@style/Theme.App"
    if current_theme == "@style/Theme.App.Starting" and existing_parent:
        old_theme = existing_parent
    target.set(f"{{{ANDROID_NS}}}theme", "@style/Theme.App.Starting")
    tree.write(path, encoding="unicode", xml_declaration=True)


def find_launcher_activity(application: ET.Element) -> ET.Element | None:
    for activity in application.findall("activity"):
        for intent in activity.findall("intent-filter"):
            actions = {item.get(f"{{{ANDROID_NS}}}name") for item in intent.findall("action")}
            categories = {item.get(f"{{{ANDROID_NS}}}name") for item in intent.findall("category")}
            if "android.intent.action.MAIN" in actions and "android.intent.category.LAUNCHER" in categories:
                return activity
    return None


def current_starting_theme_parent(res_dir: Path) -> str | None:
    for path in [res_dir / "values-v31" / "themes.xml", res_dir / "values" / "themes.xml"]:
        if not path.exists():
            continue
        match = re.search(r'<style\s+name="Theme\.App\.Starting"\s+parent="([^"]+)"', path.read_text())
        if match:
            return match.group(1)
    return None


def current_manifest_theme(root: Path, config: dict[str, Any]) -> str | None:
    path = manifest_path(root, config)
    if not path.exists():
        return None
    tree = ET.parse(path)
    application = tree.getroot().find("application")
    if application is None:
        return None
    target = find_launcher_activity(application)
    theme = (target.get(f"{{{ANDROID_NS}}}theme") if target is not None else None) or application.get(f"{{{ANDROID_NS}}}theme")
    return None if theme == "@style/Theme.App.Starting" else theme


def has_dark_splash(config: dict[str, Any]) -> bool:
    splash = splash_config(config)
    return bool(splash.get("darkImage") or splash.get("darkBackgroundColor"))


def remove_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()


def validate_duplicate_launcher_resources(res_dir: Path) -> list[str]:
    errors: list[str] = []
    for folder in DENSITIES:
        folder_path = res_dir / folder
        if (folder_path / "ic_launcher.png").exists() and (folder_path / "ic_launcher.webp").exists():
            errors.append(f"Duplicate launcher resource {folder}/ic_launcher")
        if (folder_path / "ic_launcher_round.png").exists() and (folder_path / "ic_launcher_round.webp").exists():
            errors.append(f"Duplicate launcher resource {folder}/ic_launcher_round")
    drawable = res_dir / "drawable"
    if (drawable / "ic_launcher_foreground.png").exists() and (drawable / "ic_launcher_foreground.xml").exists():
        errors.append("Duplicate launcher resource drawable/ic_launcher_foreground")
    return errors


def xml_text(root: ET.Element) -> str:
    ET.indent(root, space="    ")
    return ET.tostring(root, encoding="unicode") + "\n"
