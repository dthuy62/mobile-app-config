#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
CANONICAL = "android-mobile-config"
SKILL_NAMES = [
    "android-mobile-config",
    "android-mobile-config-init",
    "android-mobile-config-flavors",
    "android-mobile-config-assets",
    "android-mobile-config-network-security",
    "android-mobile-config-help",
]


def main() -> int:
    errors: list[str] = []
    for skill_name in SKILL_NAMES:
        validate_one_skill(SKILLS_ROOT / skill_name, skill_name, errors)

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Skills valid: {', '.join(SKILL_NAMES)}")
    return 0


def validate_one_skill(skill: Path, skill_name: str, errors: list[str]) -> None:
    skill_md = skill / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"{skill_name}: missing SKILL.md")
    else:
        frontmatter = parse_frontmatter(skill_md.read_text(), errors)
        if set(frontmatter) != {"name", "description"}:
            errors.append(f"{skill_name}: SKILL.md frontmatter must contain only name and description")
        if frontmatter.get("name") != skill_name:
            errors.append(f"{skill_name}: SKILL.md name must be {skill_name}")
        if not frontmatter.get("description"):
            errors.append(f"{skill_name}: SKILL.md description is required")

    required = ["agents/openai.yaml"]
    if skill_name == CANONICAL:
        required.extend([
            "scripts/android-mobile-config",
            "scripts/android_mobile_config/cli.py",
            "scripts/android_mobile_config/config.py",
            "scripts/android_mobile_config/gradle_kts.py",
            "scripts/android_mobile_config/resources.py",
            "scripts/android_mobile_config/assets.py",
            "scripts/android_mobile_config/network_security.py",
            "references/config-schema.md",
            "references/android-flavors.md",
            "references/android-assets.md",
            "references/network-security.md",
        ])
    for rel in required:
        if not (skill / rel).exists():
            errors.append(f"{skill_name}: missing {rel}")

    openai = skill / "agents" / "openai.yaml"
    if openai.exists() and yaml is not None:
        data = yaml.safe_load(openai.read_text())
        prompt = data.get("interface", {}).get("default_prompt", "")
        if f"${skill_name}" not in prompt:
            errors.append(f"{skill_name}: agents/openai.yaml default_prompt must mention ${skill_name}")


def parse_frontmatter(text: str, errors: list[str]) -> dict[str, str]:
    if not text.startswith("---\n"):
        errors.append("SKILL.md must start with YAML frontmatter")
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        errors.append("SKILL.md frontmatter must close with ---")
        return {}
    raw = text[4:end]
    if yaml is not None:
        data = yaml.safe_load(raw)
        return data if isinstance(data, dict) else {}
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


if __name__ == "__main__":
    raise SystemExit(main())
