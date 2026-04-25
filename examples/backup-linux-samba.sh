#!/usr/bin/env bash
set -euo pipefail

cursor-transcript-backup backup \
  --dest-root "/mnt/transcripts-2026" \
  --person-folder "Your-Name" \
  --dry-run

