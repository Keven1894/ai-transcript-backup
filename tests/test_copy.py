from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cursor_transcript_backup.copy import copy_transcripts
from cursor_transcript_backup.discover import discover_transcripts


class CopyTests(unittest.TestCase):
    def test_dry_run_does_not_create_destination(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            dest = Path(tmp) / "dest" / "Person"
            transcript = root / "project" / "agent-transcripts" / "chat-1"
            transcript.mkdir(parents=True)
            (transcript / "chat-1.jsonl").write_text("hello\n", encoding="utf-8")

            projects = discover_transcripts(root)
            summary = copy_transcripts(projects, dest, dry_run=True)

            self.assertEqual(summary.copied, 1)
            self.assertFalse(dest.exists())

    def test_copy_then_skip_on_second_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            dest = Path(tmp) / "dest" / "Person"
            transcript = root / "project" / "agent-transcripts" / "chat-1"
            (transcript / "subagents").mkdir(parents=True)
            (transcript / "chat-1.jsonl").write_text("hello\n", encoding="utf-8")
            (transcript / "subagents" / "sub-1.jsonl").write_text(
                "child\n", encoding="utf-8"
            )

            projects = discover_transcripts(root)
            first = copy_transcripts(projects, dest)
            second = copy_transcripts(projects, dest)

            self.assertEqual(first.copied, 2)
            self.assertEqual(second.skipped, 2)
            self.assertTrue((dest / "project" / "chat-1" / "chat-1.jsonl").exists())
            self.assertTrue(
                (dest / "project" / "chat-1" / "subagents" / "sub-1.jsonl").exists()
            )


if __name__ == "__main__":
    unittest.main()

