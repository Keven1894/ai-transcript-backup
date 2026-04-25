"""Discover Cursor agent transcript folders."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Transcript:
    """One Cursor parent chat transcript directory."""

    project_name: str
    transcript_id: str
    source_dir: Path
    files: tuple[Path, ...]

    @property
    def file_count(self) -> int:
        return len(self.files)


@dataclass(frozen=True)
class ProjectTranscripts:
    """Transcripts discovered under a Cursor project folder."""

    project_name: str
    project_dir: Path
    transcripts: tuple[Transcript, ...]

    @property
    def transcript_count(self) -> int:
        return len(self.transcripts)

    @property
    def file_count(self) -> int:
        return sum(t.file_count for t in self.transcripts)


def is_scratch_project(folder_name: str) -> bool:
    """Return True for Cursor scratch/temp workspace folder names."""
    if folder_name.isdigit():
        return True
    if folder_name == "c-projects":
        return True
    return folder_name.startswith("C-Users-") and "AppData-Local-Temp" in folder_name


def _files_in_transcript_dir(transcript_dir: Path) -> tuple[Path, ...]:
    return tuple(sorted(p for p in transcript_dir.rglob("*") if p.is_file()))


def discover_project_transcripts(project_dir: Path) -> ProjectTranscripts | None:
    """Discover transcript UUID folders for one Cursor project directory."""
    transcripts_dir = project_dir / "agent-transcripts"
    if not transcripts_dir.is_dir():
        return None

    transcripts: list[Transcript] = []
    for child in sorted(transcripts_dir.iterdir()):
        if not child.is_dir():
            continue
        jsonl_files = tuple(child.glob("*.jsonl"))
        if not jsonl_files:
            continue
        files = _files_in_transcript_dir(child)
        transcripts.append(
            Transcript(
                project_name=project_dir.name,
                transcript_id=child.name,
                source_dir=child,
                files=files,
            )
        )

    if not transcripts:
        return None
    return ProjectTranscripts(
        project_name=project_dir.name,
        project_dir=project_dir,
        transcripts=tuple(transcripts),
    )


def discover_transcripts(
    source_root: Path,
    *,
    include_temp: bool = False,
) -> tuple[ProjectTranscripts, ...]:
    """Discover all Cursor transcript folders under source_root."""
    if not source_root.is_dir():
        raise FileNotFoundError(f"Cursor projects folder not found: {source_root}")

    projects: list[ProjectTranscripts] = []
    for project_dir in sorted(source_root.iterdir()):
        if not project_dir.is_dir():
            continue
        if not include_temp and is_scratch_project(project_dir.name):
            continue
        project = discover_project_transcripts(project_dir)
        if project:
            projects.append(project)
    return tuple(projects)


def count_transcripts(projects: tuple[ProjectTranscripts, ...]) -> int:
    """Return total parent-chat transcript count."""
    return sum(p.transcript_count for p in projects)


def count_files(projects: tuple[ProjectTranscripts, ...]) -> int:
    """Return total transcript file count including subagents."""
    return sum(p.file_count for p in projects)

