# Contributing

Thanks for helping improve Android Mobile Config.

## Development Setup

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest
python3 scripts/validate_skill.py
```

## Guidelines

- Keep deterministic Android edits in `skill/android-mobile-config/scripts/android_mobile_config/`.
- Keep skill instructions concise; move detailed behavior to `references/`.
- Add or update pytest fixtures for Gradle/resource behavior changes.
- Run `python3 scripts/build_dist.py` before publishing a release artifact.

