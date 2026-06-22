#!/usr/bin/env python3
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills"
DIST = ROOT / "dist"


def main() -> int:
    DIST.mkdir(exist_ok=True)
    out_dir = DIST / "android-mobile-config-skills"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(SOURCE, out_dir, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
    zip_path = DIST / "android-mobile-config-skills.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(out_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(DIST))
    print(f"Built {out_dir}")
    print(f"Built {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
