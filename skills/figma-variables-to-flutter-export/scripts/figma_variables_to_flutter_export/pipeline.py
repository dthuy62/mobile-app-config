from __future__ import annotations

import json

from .colors import ColorTokenBuilder, LayerClassifier, build_base_index
from .dart_renderer import DartColorRenderer
from .models import ExportOptions, Warn
from .variables import VariableParser


class ColorExportPipeline:
    def __init__(
        self,
        *,
        parser: VariableParser | None = None,
        token_builder: ColorTokenBuilder | None = None,
        classifier: LayerClassifier | None = None,
        renderer: DartColorRenderer | None = None,
    ) -> None:
        self.parser = parser or VariableParser()
        self.token_builder = token_builder or ColorTokenBuilder()
        self.classifier = classifier or LayerClassifier()
        self.renderer = renderer or DartColorRenderer()

    def run(self, options: ExportOptions, *, warn: Warn) -> str:
        data = json.loads(options.json_file.read_text())
        variables = self.parser.parse(data)
        base_index = self._base_index(options, warn)
        tokens = self.token_builder.build(
            variables,
            strict=options.strict,
            base_index=base_index,
            warn=warn,
        )
        if not tokens:
            raise ValueError("No COLOR variables found in input JSON.")

        report = self.classifier.detect(tokens, options.layer, strict=options.strict, warn=warn)
        return self.renderer.render(
            tokens=tokens,
            layer=report.layer,
            class_prefix=options.class_prefix,
            base_class=options.base_class,
            base_import=options.base_import,
            light_mode=options.light_mode,
            dark_mode=options.dark_mode,
            exclude_material_extension=options.exclude_material_extension,
        )

    def _base_index(self, options: ExportOptions, warn: Warn) -> dict[str, str] | None:
        if options.base_json is None:
            return None
        base_data = json.loads(options.base_json.read_text())
        base_variables = self.parser.parse(base_data)
        return build_base_index(base_variables, warn)

