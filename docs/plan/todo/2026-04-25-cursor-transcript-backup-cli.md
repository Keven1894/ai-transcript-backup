# Cursor Transcript Backup CLI — Todo Plan

**Date:** 2026-04-25
**Repo:** `C:/projects/cursor-transcript-backup`
**Status:** Draft / implementation starting
**Goal:** Build a small standalone CLI tool that automatically finds Cursor
agent transcripts on a user's machine and backs them up into a user-defined
folder on a shared/network drive.

---

## 1. Problem

Cursor agent transcripts are valuable research and operations records, but they
live in local per-user Cursor state:

```text
~/.cursor/projects/<project-folder>/agent-transcripts/<chat-uuid>/<chat-uuid>.jsonl
~/.cursor/projects/<project-folder>/agent-transcripts/<chat-uuid>/subagents/<subagent-uuid>.jsonl
```

Manual copying is error-prone:

- users may not know where Cursor stores transcripts;
- some transcripts include nested `subagents/` files;
- Windows network paths vary (`T:\...` vs `\\server\share\...`);
- repeated backups should not duplicate work;
- each person needs their own folder on the shared drive.

---

## 2. Initial Scope

### In scope for v0.1

- Python CLI tool, standard library only.
- Automatically discover Cursor transcripts from:
  - default: `Path.home() / ".cursor" / "projects"`
  - override: `--source-root`
- Copy transcript folders into:
  - `--dest-root`
  - `--person-folder`
- Preserve Cursor's hierarchy:

```text
<dest-root>/<person-folder>/<project-folder>/<chat-uuid>/<chat-uuid>.jsonl
<dest-root>/<person-folder>/<project-folder>/<chat-uuid>/subagents/<subagent-uuid>.jsonl
```

- Support destination forms:
  - Windows drive-letter network mount: `T:\Transcripts-2026`
  - Windows UNC path: `\\dpantherfi03.fiu.edu\Transcripts-2026`
  - Linux / Samba mount path: `/mnt/transcripts-2026`
- Dry run mode.
- Idempotent copy:
  - skip files with matching size + mtime
  - copy new files
  - update changed files
- Skip Cursor scratch/temp workspaces by default.
- Print clear run summary:
  - project count
  - chat transcript count
  - copied / updated / skipped / errors
- Optional JSON manifest output.

### Out of scope for v0.1

- Cursor SQLite chat history export from `workspaceStorage/state.vscdb`.
- Cloud upload.
- Scheduling / daemon mode.
- GUI.
- Authentication or mounting shares for the user. The share must already be
  mounted / reachable by the shell running the CLI.

---

## 3. Proposed CLI

### Main command

```bash
cursor-transcript-backup backup \
  --dest-root "T:\Transcripts-2026" \
  --person-folder "Boyuan-Keven-Guan"
```

### UNC example

```bash
cursor-transcript-backup backup \
  --dest-root "\\dpantherfi03.fiu.edu\Transcripts-2026" \
  --person-folder "Boyuan-Keven-Guan"
```

### Linux / Samba mount example

```bash
cursor-transcript-backup backup \
  --dest-root "/mnt/transcripts-2026" \
  --person-folder "Boyuan-Keven-Guan"
```

### Useful flags

| Flag | Purpose |
|---|---|
| `--dest-root <path>` | Required. Shared drive root. |
| `--person-folder <name>` | Required. User-specific folder under destination root. |
| `--source-root <path>` | Optional. Defaults to `~/.cursor/projects`. |
| `--dry-run` | Print what would be copied without writing. |
| `--include-temp` | Include Cursor scratch/temp workspaces. |
| `--manifest` | Write `manifest.json` under the destination person folder. |
| `--verbose` | Print every copied/skipped file. |

---

## 4. Repo Structure

```text
cursor-transcript-backup/
  README.md
  pyproject.toml
  src/
    cursor_transcript_backup/
      __init__.py
      cli.py
      discover.py
      copy.py
      paths.py
      manifest.py
  tests/
    test_discover.py
    test_paths.py
  examples/
    backup-windows-drive.ps1
    backup-windows-unc.ps1
    backup-linux-samba.sh
  docs/
    plan/
      todo/
        2026-04-25-cursor-transcript-backup-cli.md
```

---

## 5. Implementation Plan

### Phase 1 — Repo scaffold

- [x] Create standalone repo at `C:/projects/cursor-transcript-backup`.
- [x] Initialize git.
- [x] Add this todo plan.
- [x] Add `README.md`.
- [x] Add `pyproject.toml`.
- [x] Add package skeleton under `src/cursor_transcript_backup/`.

### Phase 2 — Discovery

- [x] Implement `paths.py`.
  - [x] Resolve default source root with `Path.home() / ".cursor" / "projects"`.
  - [x] Normalize destination root without trying to mount it.
  - [x] Validate `person-folder` does not contain path separators.
- [x] Implement `discover.py`.
  - [x] Iterate project folders.
  - [x] Skip temp/scratch folders unless `--include-temp`.
  - [x] Detect transcript UUID folders containing at least one `.jsonl`.
  - [x] Preserve nested `subagents/` files.
- [x] Add discovery unit tests using temporary fake Cursor project trees.

### Phase 3 — Copy engine

- [x] Implement `copy.py`.
  - [x] Copy all files under each transcript UUID folder.
  - [x] Use `shutil.copy2`.
  - [x] Compare size + whole-second mtime for skip behavior.
  - [x] Accumulate copied / updated / skipped / error counts.
- [x] Ensure dry run never creates destination folders.
- [x] Add tests for copied / skipped / updated behavior.

### Phase 4 — CLI

- [x] Implement `cli.py` with `argparse`.
- [ ] Commands:
  - [x] `backup`
  - [x] optional `scan` command for discovery-only output
- [x] Exit codes:
  - [x] `0` success
  - [x] `1` copy errors
  - [x] `2` invalid source
  - [x] `3` invalid destination / cannot create destination
- [x] Pretty console summary.
- [x] `--verbose` file-level output.

### Phase 5 — Manifest

- [x] Implement `manifest.py`.
- [x] Optional `--manifest` writes:

```json
{
  "tool": "cursor-transcript-backup",
  "version": "0.1.0",
  "started_at": "...",
  "source_root": "...",
  "dest_root": "...",
  "person_folder": "...",
  "projects": [],
  "totals": {
    "projects": 0,
    "transcripts": 0,
    "files_copied": 0,
    "files_updated": 0,
    "files_skipped": 0,
    "errors": 0
  }
}
```

### Phase 6 — Examples + docs

- [x] Add Windows drive-letter PowerShell example.
- [x] Add Windows UNC PowerShell example.
- [x] Add Linux Samba mount shell example.
- [x] README includes:
  - [x] quick start
  - [x] destination path examples
  - [x] dry-run-first recommendation
  - [x] privacy warning: do not commit transcripts to git
  - [x] troubleshooting: network share visible in Explorer but not shell

### Phase 7 — Validation

- [x] Run unit tests.
- [x] Run local dry-run against real Cursor transcripts.
- [x] Run real copy to a temporary local folder.
- [ ] If available, run real copy to `T:\Transcripts-2026\Boyuan-Keven-Guan`.
- [ ] Commit initial version.

---

## 6. Design Decisions

### Keep source discovery automatic

The user should not need to know Cursor internals. By default, the tool uses:

```python
Path.home() / ".cursor" / "projects"
```

This matches Windows, macOS, and Linux for Cursor's newer
`agent-transcripts/` storage.

### Keep destination explicit

The tool should not guess or mount network shares. The user must provide
`--dest-root`. This avoids hidden credentials, OS-specific mount commands, and
surprising writes.

### Preserve hierarchy

Do not flatten transcripts. Parent chats and subagent transcripts have a real
relationship in Cursor's file layout, and downstream analysis needs that tree.

### Do not copy unrelated Cursor state

Only copy `agent-transcripts/`. Exclude `terminals/`, `assets/`, `canvases/`,
`rules/`, `uploads/`, etc.

### No third-party dependencies initially

The first version should run with system Python on a team member's laptop.
Packaging can come later.

---

## 7. Open Questions

- Should `--person-folder` allow spaces, or should we recommend
  `First-Last` / `First-Middle-Last` only?
- Should `--manifest` be default-on for research provenance?
- Should we add a `--since` filter later for incremental date-based backups,
  or is size+mtime skipping enough?
- Should the tool include a redaction / sensitive-term scan later, or leave
  privacy review outside the backup step?

---

## 8. Success Criteria

v0.1 is complete when:

- A user can run one command on Windows with either `T:\...` or
  `\\server\share\...`.
- The tool automatically finds all local Cursor agent transcripts.
- The copy preserves project/chat/subagent hierarchy.
- Re-running the command skips already-synced files.
- Dry-run output is clear enough for non-expert users.
- README gives enough guidance for team members to run it without editing code.
