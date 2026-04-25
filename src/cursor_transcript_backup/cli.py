"""Command-line interface for cursor-transcript-backup."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .copy import copy_transcripts
from .discover import count_files, count_transcripts, discover_transcripts
from .manifest import build_manifest, write_manifest
from .paths import (
    PathValidationError,
    destination_person_root,
    resolve_source_root,
    validate_person_folder,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cursor-transcript-backup",
        description="Back up Cursor agent transcripts to a shared/network drive.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    backup = subcommands.add_parser(
        "backup",
        help="Discover local Cursor transcripts and copy them to a destination.",
    )
    backup.add_argument("--dest-root", required=True, help="Shared drive root.")
    backup.add_argument(
        "--person-folder",
        required=True,
        help="User-specific folder under the destination root.",
    )
    backup.add_argument(
        "--source-root",
        default=None,
        help="Override Cursor projects root. Defaults to ~/.cursor/projects.",
    )
    backup.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be copied without writing files.",
    )
    backup.add_argument(
        "--include-temp",
        action="store_true",
        help="Include Cursor scratch/temp workspaces.",
    )
    backup.add_argument(
        "--manifest",
        action="store_true",
        help="Write a JSON manifest under the destination person folder.",
    )
    backup.add_argument(
        "--verbose",
        action="store_true",
        help="Print file-level copy/skip decisions.",
    )
    scan = subcommands.add_parser(
        "scan",
        help="Discover local Cursor transcripts without copying.",
    )
    scan.add_argument(
        "--source-root",
        default=None,
        help="Override Cursor projects root. Defaults to ~/.cursor/projects.",
    )
    scan.add_argument(
        "--include-temp",
        action="store_true",
        help="Include Cursor scratch/temp workspaces.",
    )
    return parser


def print_discovery(projects) -> None:
    for project in projects:
        print(
            f"  {project.project_name:<60} "
            f"transcripts={project.transcript_count:<3} files={project.file_count:<3}"
        )


def run_scan(args: argparse.Namespace) -> int:
    source_root = resolve_source_root(args.source_root)
    try:
        projects = discover_transcripts(source_root, include_temp=args.include_temp)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"source: {source_root}")
    print(
        f"found:  {len(projects)} project(s), "
        f"{count_transcripts(projects)} transcript(s), {count_files(projects)} file(s)"
    )
    print("-" * 70)
    print_discovery(projects)
    return 0


def run_backup(args: argparse.Namespace) -> int:
    try:
        person_folder = validate_person_folder(args.person_folder)
        source_root = resolve_source_root(args.source_root)
        dest_person_root = destination_person_root(args.dest_root, person_folder)
    except PathValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    try:
        projects = discover_transcripts(source_root, include_temp=args.include_temp)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    mode = "DRY RUN" if args.dry_run else "COPY"
    print(f"[{mode}] source:      {source_root}")
    print(f"[{mode}] destination: {dest_person_root}")
    print(
        f"[{mode}] {len(projects)} project(s), "
        f"{count_transcripts(projects)} transcript(s), {count_files(projects)} file(s)"
    )
    print("-" * 70)

    try:
        summary = copy_transcripts(
            projects,
            dest_person_root,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )
    except OSError as exc:
        print(f"ERROR: cannot create destination {dest_person_root}: {exc}", file=sys.stderr)
        return 3

    for project in summary.projects:
        print(
            f"  {project.project_name:<60} "
            f"transcripts={project.transcripts:<3} "
            f"copied={project.copied:<3} "
            f"updated={project.updated:<3} "
            f"skipped={project.skipped:<3} "
            f"errors={len(project.errors):<3}"
        )

    if args.verbose and summary.actions:
        print("-" * 70)
        for action in summary.actions:
            suffix = f" ({action.error})" if action.error else ""
            print(f"{action.action:<7} {action.source} -> {action.destination}{suffix}")

    print("-" * 70)
    print(
        f"TOTAL  copied={summary.copied}  updated={summary.updated}  "
        f"skipped={summary.skipped}  errors={summary.error_count}"
    )

    if args.manifest:
        data = build_manifest(
            source_root=source_root,
            dest_person_root=dest_person_root,
            person_folder=person_folder,
            projects=projects,
            summary=summary,
            dry_run=args.dry_run,
        )
        manifest_path = (
            Path.cwd() / "cursor-transcript-backup-manifest.dry-run.json"
            if args.dry_run
            else dest_person_root / "manifest.json"
        )
        write_manifest(manifest_path, data)
        print(f"manifest: {manifest_path}")

    if summary.errors:
        print("\nErrors:", file=sys.stderr)
        for error in summary.errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "backup":
        return run_backup(args)
    if args.command == "scan":
        return run_scan(args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

