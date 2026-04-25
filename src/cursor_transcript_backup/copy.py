"""Copy Cursor transcript folders to a backup destination."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .discover import ProjectTranscripts, Transcript


@dataclass
class FileAction:
    """Copy decision for one file."""

    source: Path
    destination: Path
    action: str
    error: str | None = None


@dataclass
class ProjectCopySummary:
    """Copy summary for one project."""

    project_name: str
    transcripts: int = 0
    copied: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class CopySummary:
    """Copy summary for a complete run."""

    projects: list[ProjectCopySummary] = field(default_factory=list)
    actions: list[FileAction] = field(default_factory=list)

    @property
    def project_count(self) -> int:
        return len(self.projects)

    @property
    def transcript_count(self) -> int:
        return sum(p.transcripts for p in self.projects)

    @property
    def copied(self) -> int:
        return sum(p.copied for p in self.projects)

    @property
    def updated(self) -> int:
        return sum(p.updated for p in self.projects)

    @property
    def skipped(self) -> int:
        return sum(p.skipped for p in self.projects)

    @property
    def errors(self) -> list[str]:
        out: list[str] = []
        for project in self.projects:
            out.extend(project.errors)
        return out

    @property
    def error_count(self) -> int:
        return len(self.errors)


def files_are_equal(src: Path, dst: Path) -> bool:
    """Cheap equality check: same size and same mtime rounded to seconds."""
    if not dst.exists():
        return False
    src_stat = src.stat()
    dst_stat = dst.stat()
    return (
        src_stat.st_size == dst_stat.st_size
        and int(src_stat.st_mtime) == int(dst_stat.st_mtime)
    )


def destination_for_file(
    transcript: Transcript,
    src_file: Path,
    dest_person_root: Path,
) -> Path:
    """Map a source transcript file to its backup destination."""
    rel = src_file.relative_to(transcript.source_dir)
    return (
        dest_person_root
        / transcript.project_name
        / transcript.transcript_id
        / rel
    )


def copy_file(src: Path, dst: Path, *, dry_run: bool) -> str:
    """Copy one file if needed and return copied/updated/skipped."""
    if files_are_equal(src, dst):
        return "skipped"
    action = "updated" if dst.exists() else "copied"
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return action


def copy_transcripts(
    projects: tuple[ProjectTranscripts, ...],
    dest_person_root: Path,
    *,
    dry_run: bool = False,
    verbose: bool = False,
) -> CopySummary:
    """Copy discovered transcripts into dest_person_root."""
    summary = CopySummary()

    if not dry_run:
        dest_person_root.mkdir(parents=True, exist_ok=True)

    for project in projects:
        project_summary = ProjectCopySummary(
            project_name=project.project_name,
            transcripts=project.transcript_count,
        )
        for transcript in project.transcripts:
            for src_file in transcript.files:
                dst_file = destination_for_file(transcript, src_file, dest_person_root)
                try:
                    action = copy_file(src_file, dst_file, dry_run=dry_run)
                except OSError as exc:
                    error = f"{src_file} -> {dst_file}: {exc}"
                    project_summary.errors.append(error)
                    if verbose:
                        summary.actions.append(
                            FileAction(src_file, dst_file, "error", error)
                        )
                    continue

                if action == "copied":
                    project_summary.copied += 1
                elif action == "updated":
                    project_summary.updated += 1
                elif action == "skipped":
                    project_summary.skipped += 1

                if verbose:
                    summary.actions.append(FileAction(src_file, dst_file, action))

        summary.projects.append(project_summary)

    return summary

