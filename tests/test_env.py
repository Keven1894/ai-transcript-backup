from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cursor_transcript_backup.env import parse_env_file


class EnvTests(unittest.TestCase):
    def test_parse_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text(
                "\n".join(
                    [
                        "# comment",
                        "CURSOR_TRANSCRIPT_DEST_ROOT='\\\\server\\share'",
                        'CURSOR_TRANSCRIPT_PERSON_FOLDER="Your-Name"',
                        "CURSOR_TRANSCRIPT_SOURCE_ROOT=~/custom-source",
                    ]
                ),
                encoding="utf-8",
            )

            values = parse_env_file(path)

            self.assertEqual(
                values["CURSOR_TRANSCRIPT_DEST_ROOT"], r"\\server\share"
            )
            self.assertEqual(values["CURSOR_TRANSCRIPT_PERSON_FOLDER"], "Your-Name")
            self.assertEqual(values["CURSOR_TRANSCRIPT_SOURCE_ROOT"], "~/custom-source")


if __name__ == "__main__":
    unittest.main()

