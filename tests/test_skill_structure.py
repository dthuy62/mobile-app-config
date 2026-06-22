from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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
    text = (ROOT / "skills" / "android-mobile-config" / "SKILL.md").read_text()
    frontmatter = text.split("---", 2)[1]
    keys = [line.split(":", 1)[0] for line in frontmatter.strip().splitlines()]
    assert keys == ["name", "description"]


def test_plugin_manifests_exist() -> None:
    assert (ROOT / ".codex-plugin" / "plugin.json").exists()
    assert (ROOT / ".claude-plugin" / "plugin.json").exists()
    assert (ROOT / ".agents" / "plugins" / "marketplace.json").exists()


def test_build_dist_contains_only_portable_skill_files() -> None:
    result = subprocess.run(
        ["python3", str(ROOT / "scripts" / "build_dist.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    zip_path = ROOT / "dist" / "android-mobile-config-skills.zip"
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
    assert "android-mobile-config-skills/android-mobile-config/SKILL.md" in names
    assert "android-mobile-config-skills/android-mobile-config-flavors/SKILL.md" in names
    assert "android-mobile-config-skills/android-mobile-config-assets/SKILL.md" in names
    assert all("/tests/" not in name for name in names)
    assert all("__pycache__" not in name for name in names)
    assert all(not name.endswith(".pyc") for name in names)
