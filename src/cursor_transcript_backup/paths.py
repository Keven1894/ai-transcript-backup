"""Path helpers for Cursor transcript backup."""

from __future__ import annotations

import os
from pathlib import Path


class PathValidationError(ValueError):
    """Raised when user-provided paths are invalid."""


def default_cursor_projects_root() -> Path:
    """Return Cursor's per-project local state root."""
    return Path.home() / ".cursor" / "projects"


def resolve_source_root(source_root: str | None = None) -> Path:
    """Resolve the source root, defaulting to ~/.cursor/projects."""
    path = Path(source_root).expanduser() if source_root else default_cursor_projects_root()
    return path


def validate_person_folder(name: str) -> str:
    """Validate a single destination sub-folder name."""
    if not name or not name.strip():
        raise PathValidationError("--person-folder cannot be empty")

    stripped = name.strip()
    separators = {"/", "\\"}
    if os.sep:
        separators.add(os.sep)
    if os.altsep:
        separators.add(os.altsep)

    if any(sep in stripped for sep in separators):
        raise PathValidationError(
            "--person-folder must be a single folder name, not a path"
        )
    if stripped in {".", ".."}:
        raise PathValidationError("--person-folder cannot be '.' or '..'")
    return stripped


def resolve_destination_root(dest_root: str) -> Path:
    """Resolve a user-provided destination root without trying to mount it."""
    if not dest_root or not dest_root.strip():
        raise PathValidationError("--dest-root cannot be empty")
    return Path(dest_root).expanduser()


def destination_person_root(dest_root: str, person_folder: str) -> Path:
    """Return <dest-root>/<person-folder> after validating inputs."""
    return resolve_destination_root(dest_root) / validate_person_folder(person_folder)

