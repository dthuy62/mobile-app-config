# Contributing

Thanks for helping improve Mobile App Config.

## Development Setup

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest
python3 scripts/validate_skill.py
```

## Guidelines

- Keep deterministic Android edits in `skills/android/scripts/android_mobile_config/`.
- Keep skill instructions concise; move detailed behavior to `references/`.
- Add or update pytest fixtures for Gradle/resource behavior changes.
