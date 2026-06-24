from __future__ import annotations

import subprocess
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = [
    "android",
    "android-init",
    "android-flavors",
    "android-firebase",
    "android-assets",
    "android-network-security",
    "android-help",
]


def test_validate_skill_script_passes() -> None:
    result = subprocess.run(
        ["python3", str(ROOT / "scripts" / "validate_skill.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_skill_frontmatter_contains_only_name_and_description() -> None:
    text = (ROOT / "skills" / "android" / "SKILL.md").read_text()
    frontmatter = text.split("---", 2)[1]
    keys = [line.split(":", 1)[0] for line in frontmatter.strip().splitlines()]
    assert keys == ["name", "description"]


def test_plugin_manifests_exist() -> None:
    assert (ROOT / ".codex-plugin" / "plugin.json").exists()
    assert (ROOT / ".claude-plugin" / "plugin.json").exists()
    assert (ROOT / ".agents" / "plugins" / "marketplace.json").exists()


def test_plugin_brand_is_mobile_app_config() -> None:
    import json

    codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
    claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert codex["name"] == "mobile-app-config"
    assert claude["name"] == "mobile-app-config"
    assert "mobile-app-config" in (ROOT / "pyproject.toml").read_text()
    assert (ROOT / "skills" / "android" / "scripts" / "mobile-app-config").exists()


def test_skill_docs_do_not_depend_on_local_install_paths() -> None:
    forbidden = ["~/.codex/skills", "/Users/", ".codex/plugins/cache", "android-mobile-config"]
    for path in (ROOT / "skills").glob("*/SKILL.md"):
        text = path.read_text()
        for value in forbidden:
            assert value not in text, f"{path} contains unsupported install path or stale name: {value}"


def test_skill_cli_paths_resolve_inside_marketplace_layout(tmp_path) -> None:
    cache_skills = tmp_path / "plugins" / "cache" / "mobile-app-config" / "mobile-app-config" / "1.0.0" / "skills"
    for skill_name in SKILL_NAMES:
        source = ROOT / "skills" / skill_name
        target = cache_skills / skill_name
        target.mkdir(parents=True)
        for child in source.iterdir():
            if child.is_file():
                (target / child.name).write_bytes(child.read_bytes())
            elif child.name in {"scripts", "agents", "references"}:
                shutil.copytree(child, target / child.name)

    expected = {
        "android": "scripts/mobile-app-config",
        "android-init": "../android/scripts/mobile-app-config",
        "android-flavors": "../android/scripts/mobile-app-config",
        "android-firebase": "../android/scripts/mobile-app-config",
        "android-assets": "../android/scripts/mobile-app-config",
        "android-network-security": "../android/scripts/mobile-app-config",
        "android-help": "../android/scripts/mobile-app-config",
    }
    for skill_name, rel in expected.items():
        assert rel in (ROOT / "skills" / skill_name / "SKILL.md").read_text()
        assert (cache_skills / skill_name / rel).resolve().exists()


def test_public_docs_document_only_supported_install_flows() -> None:
    text = "\n".join((ROOT / name).read_text() for name in ["README.md", "CONTRIBUTING.md"])
    forbidden = [
        "android-mobile-config",
        "Codex Skill Manual",
        "install_local_symlinks.py",
        "~/.codex/skills",
        "Other AI Coding Tools",
        "Platform Output Directories",
        "build_dist.py",
    ]
    for value in forbidden:
        assert value not in text
