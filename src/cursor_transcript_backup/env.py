"""Minimal .env support without third-party dependencies."""

from __future__ import annotations

import os
from pathlib import Path


DEFAULT_ENV_FILE = ".env"


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a small KEY=VALUE .env file."""
    values: dict[str, str] = {}
    if not path.is_file():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in {"'", '"'}
        ):
            value = value[1:-1]
        values[key] = value
    return values


def load_env(path: str | None = None) -> dict[str, str]:
    """Load config from process env overlaid on a local .env file."""
    env_path = Path(path or DEFAULT_ENV_FILE).expanduser()
    values = parse_env_file(env_path)
    for key in (
        "CURSOR_TRANSCRIPT_DEST_ROOT",
        "CURSOR_TRANSCRIPT_PERSON_FOLDER",
        "CURSOR_TRANSCRIPT_SOURCE_ROOT",
    ):
        if os.environ.get(key):
            values[key] = os.environ[key]
    return values

