"""JSON manifest output for transcript backup runs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .copy import CopySummary
from .discover import ProjectTranscripts


def build_manifest(
    *,
    source_root: Path,
    dest_person_root: Path,
    person_folder: str,
    projects: tuple[ProjectTranscripts, ...],
    summary: CopySummary,
    dry_run: bool,
) -> dict[str, Any]:
    """Build a machine-readable manifest for one run."""
    return {
        "tool": "cursor-transcript-backup",
        "version": __version__,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "source_root": str(source_root),
        "destination": str(dest_person_root),
        "person_folder": person_folder,
        "projects": [
            {
                "name": project.project_name,
                "transcripts": project.transcript_count,
                "files": project.file_count,
            }
            for project in projects
        ],
        "totals": {
            "projects": summary.project_count,
            "transcripts": summary.transcript_count,
            "files_copied": summary.copied,
            "files_updated": summary.updated,
            "files_skipped": summary.skipped,
            "errors": summary.error_count,
        },
        "errors": summary.errors,
    }


def write_manifest(path: Path, data: dict[str, Any]) -> None:
    """Write manifest JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

