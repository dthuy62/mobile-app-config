from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "skills" / "android-mobile-config" / "scripts" / "android-mobile-config"


def copy_fixture(tmp_path: Path, name: str) -> Path:
    source = ROOT / "tests" / "fixtures" / name
    target = tmp_path / name
    shutil.copytree(source, target)
    return target


def run_cli(project: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(CLI), "--root", str(project), *args],
        cwd=project,
        text=True,
        capture_output=True,
        check=False,
    )


def read_config(project: Path) -> dict:
    return json.loads((project / "android-mobile-config.json").read_text())
