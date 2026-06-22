#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
LOCAL_SKILLS = Path.home() / ".codex" / "skills"

SKILL_NAMES = [
    "android-mobile-config",
    "android-mobile-config-init",
    "android-mobile-config-flavors",
    "android-mobile-config-assets",
    "android-mobile-config-network-security",
    "android-mobile-config-help",
]


def main() -> int:
    LOCAL_SKILLS.mkdir(parents=True, exist_ok=True)
    for name in SKILL_NAMES:
        source = SKILLS_ROOT / name
        target = LOCAL_SKILLS / name
        if not source.exists():
            raise SystemExit(f"missing source skill: {source}")
        if target.exists() or target.is_symlink():
            if target.is_symlink() or target.is_file():
                target.unlink()
            else:
                raise SystemExit(f"refusing to replace directory: {target}")
        os.symlink(source, target)
        print(f"{target} -> {source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
