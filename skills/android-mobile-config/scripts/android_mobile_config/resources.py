from __future__ import annotations

from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape


def write_flavor_app_names(root: Path, config: dict[str, Any]) -> None:
    module = config["module"]
    for flavor, flavor_config in config["flavors"].items():
        values_dir = root / module / "src" / flavor / "res" / "values"
        values_dir.mkdir(parents=True, exist_ok=True)
        strings_path = values_dir / "strings.xml"
        app_name = flavor_config.get("appName", flavor)
        strings_path.write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            "<resources>\n"
            f'    <string name="app_name">{escape(str(app_name))}</string>\n'
            "</resources>\n"
        )

