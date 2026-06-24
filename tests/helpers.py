from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "skills" / "android" / "scripts" / "mobile-app-config"


def copy_fixture(tmp_path: Path, name: str) -> Path:
    source = ROOT / "tests" / "fixtures" / name
    target = tmp_path / name
    shutil.copytree(source, target)
    return target


def run_cli(project: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), "--root", str(project), *args],
        cwd=project,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def read_config(project: Path) -> dict:
    return json.loads((project / "android-app-config.json").read_text())
