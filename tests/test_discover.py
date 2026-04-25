from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cursor_transcript_backup.discover import (
    count_files,
    count_transcripts,
    discover_transcripts,
    is_scratch_project,
)


class DiscoverTests(unittest.TestCase):
    def test_scratch_project_patterns(self) -> None:
        self.assertTrue(is_scratch_project("1776272492094"))
        self.assertTrue(
            is_scratch_project("C-Users-bguan-AppData-Local-Temp-abc")
        )
        self.assertTrue(is_scratch_project("c-projects"))
        self.assertFalse(is_scratch_project("c-projects-envistor-data"))

    def test_discovers_parent_and_subagent_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            transcript = (
                root
                / "c-projects-example"
                / "agent-transcripts"
                / "chat-1"
            )
            (transcript / "subagents").mkdir(parents=True)
            (transcript / "chat-1.jsonl").write_text("parent\n", encoding="utf-8")
            (transcript / "subagents" / "sub-1.jsonl").write_text(
                "child\n", encoding="utf-8"
            )

            projects = discover_transcripts(root)

            self.assertEqual(len(projects), 1)
            self.assertEqual(projects[0].project_name, "c-projects-example")
            self.assertEqual(count_transcripts(projects), 1)
            self.assertEqual(count_files(projects), 2)
            self.assertEqual(projects[0].transcripts[0].transcript_id, "chat-1")

    def test_skips_temp_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            transcript = root / "1776272492094" / "agent-transcripts" / "chat-1"
            transcript.mkdir(parents=True)
            (transcript / "chat-1.jsonl").write_text("parent\n", encoding="utf-8")

            self.assertEqual(discover_transcripts(root), ())
            self.assertEqual(len(discover_transcripts(root, include_temp=True)), 1)


if __name__ == "__main__":
    unittest.main()

