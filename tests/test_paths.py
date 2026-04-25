from __future__ import annotations

import unittest

from cursor_transcript_backup.paths import PathValidationError, validate_person_folder


class PersonFolderTests(unittest.TestCase):
    def test_accepts_simple_folder_name(self) -> None:
        self.assertEqual(validate_person_folder("Boyuan-Keven-Guan"), "Boyuan-Keven-Guan")

    def test_strips_surrounding_whitespace(self) -> None:
        self.assertEqual(validate_person_folder("  Taylor-Bonachea  "), "Taylor-Bonachea")

    def test_rejects_empty(self) -> None:
        with self.assertRaises(PathValidationError):
            validate_person_folder(" ")

    def test_rejects_path_separators(self) -> None:
        for value in ("Team/Person", r"Team\Person"):
            with self.subTest(value=value):
                with self.assertRaises(PathValidationError):
                    validate_person_folder(value)

    def test_rejects_dot_segments(self) -> None:
        for value in (".", ".."):
            with self.subTest(value=value):
                with self.assertRaises(PathValidationError):
                    validate_person_folder(value)


if __name__ == "__main__":
    unittest.main()

