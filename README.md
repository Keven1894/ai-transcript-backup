# Cursor Transcript Backup

Lightweight backup and archival tooling for local AI agent transcripts,
starting with Cursor and network/shared drives.

Cursor stores agent conversations locally under:

```text
~/.cursor/projects/<project-folder>/agent-transcripts/<chat-uuid>/<chat-uuid>.jsonl
~/.cursor/projects/<project-folder>/agent-transcripts/<chat-uuid>/subagents/<subagent-uuid>.jsonl
```

This tool finds those transcripts automatically and copies them into a
user-defined folder on a network/shared drive while preserving the project,
chat UUID, and subagent hierarchy.

## Features

- automatically discover `~/.cursor/projects/*/agent-transcripts/`
- preserve project / chat UUID / subagent hierarchy
- support Windows drive-letter paths, Windows UNC paths, and Linux Samba mount
  paths as destinations
- provide dry-run and idempotent re-run behavior
- write an optional JSON manifest for provenance
- skip Cursor scratch/temp workspaces by default

## Install For Local Development

```bash
git clone <repo-url>
cd cursor-transcript-backup
python -m pip install -e .
```

You can also run without installing:

```bash
PYTHONPATH=src python -m cursor_transcript_backup.cli --help
```

## Quick Start

Always dry-run first.

### Windows Network Drive

```powershell
cursor-transcript-backup backup `
  --dest-root "T:\Transcripts-2026" `
  --person-folder "Boyuan-Keven-Guan" `
  --dry-run
```

Then run without `--dry-run`:

```powershell
cursor-transcript-backup backup `
  --dest-root "T:\Transcripts-2026" `
  --person-folder "Boyuan-Keven-Guan" `
  --manifest
```

### Windows UNC Path

```powershell
cursor-transcript-backup backup `
  --dest-root "\\dpantherfi03.fiu.edu\Transcripts-2026" `
  --person-folder "Boyuan-Keven-Guan" `
  --dry-run
```

### Linux / Samba Mount

```bash
cursor-transcript-backup backup \
  --dest-root "/mnt/transcripts-2026" \
  --person-folder "Boyuan-Keven-Guan" \
  --dry-run
```

## Scan Only

```bash
cursor-transcript-backup scan
```

This prints discovered projects, parent chat transcript counts, and total
transcript files including subagents.

## Destination Layout

```text
<dest-root>/<person-folder>/
  <project-folder>/
    <chat-uuid>/
      <chat-uuid>.jsonl
      subagents/
        <subagent-uuid>.jsonl
```

## Useful Flags

| Flag | Purpose |
|---|---|
| `--dest-root <path>` | Shared drive root. Required for `backup`. |
| `--person-folder <name>` | User-specific folder under destination root. Required for `backup`. |
| `--source-root <path>` | Override source root. Defaults to `~/.cursor/projects`. |
| `--dry-run` | Show what would be copied without writing transcript files. |
| `--include-temp` | Include Cursor scratch/temp workspaces. |
| `--manifest` | Write `manifest.json` under the destination person folder. |
| `--verbose` | Print file-level copy/skip decisions. |

## Privacy

Do not commit transcript backups to git. Transcripts may contain private
project context, copied secrets, personal information, or unpublished research
notes. Store them only in the intended local or shared archive location.

## Troubleshooting

### The network drive works in File Explorer but not in the shell

Windows drive-letter mappings can be session-specific. If `T:\...` hangs or is
not found from a background shell, open a normal PowerShell or Command Prompt
window and run the command there. UNC paths may also work:

```powershell
--dest-root "\\server\share"
```

### The tool says "No transcripts found"

Check the source root:

```bash
cursor-transcript-backup scan
```

If Cursor has never created agent transcripts on that machine, there may be
nothing to back up yet.

See the implementation plan:

- `docs/plan/todo/2026-04-25-cursor-transcript-backup-cli.md`
