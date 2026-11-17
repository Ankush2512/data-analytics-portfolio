import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import library_management as app


class LibraryManagementTests(unittest.TestCase):
    def setUp(self):
        self.library = {}

    def test_add_book_normalizes_id_and_trims_fields(self):
        self.assertTrue(app.add_book(self.library, " b001 ", " Python Basics ", " A. Author "))
        self.assertEqual(self.library["B001"]["title"], "Python Basics")

    def test_reject_duplicate_id_and_case_insensitive_title(self):
        app.add_book(self.library, "B001", "Python Basics", "A. Author")
        self.assertFalse(app.add_book(self.library, "B001", "Another Book", "B. Author"))
        self.assertFalse(app.add_book(self.library, "B002", "python basics", "B. Author"))

    def test_reject_blank_required_fields(self):
        self.assertFalse(app.add_book(self.library, "", "Title", "Author"))
        self.assertFalse(app.add_book(self.library, "B001", "  ", "Author"))
        self.assertFalse(app.add_book(self.library, "B001", "Title", "  "))

    def test_issue_and_return_book(self):
        app.add_book(self.library, "B001", "Python Basics", "A. Author")
        self.assertTrue(app.issue_book(self.library, "B001", "Ankush"))
        self.assertFalse(app.issue_book(self.library, "B001", "Another Borrower"))
        self.assertEqual(self.library["B001"]["issued_to"], "Ankush")
        self.assertTrue(app.return_book(self.library, "B001"))
        self.assertTrue(self.library["B001"]["available"])
        self.assertIsNone(self.library["B001"]["issued_to"])

    def test_reject_unknown_book_and_blank_borrower(self):
        self.assertFalse(app.issue_book(self.library, "MISSING", "Ankush"))
        app.add_book(self.library, "B001", "Python Basics", "A. Author")
        self.assertFalse(app.issue_book(self.library, "B001", "  "))
        self.assertFalse(app.return_book(self.library, "MISSING"))

    def test_modify_book_and_reject_duplicate_title(self):
        app.add_book(self.library, "B001", "Python Basics", "A. Author")
        app.add_book(self.library, "B002", "Data Science", "B. Author")
        self.assertTrue(app.modify_book(self.library, "B001", "Python for Beginners", "A. Author"))
        self.assertFalse(app.modify_book(self.library, "B001", "Data Science", "A. Author"))
        self.assertFalse(app.modify_book(self.library, "MISSING", "New Title", "Author"))

    def test_json_save_and_reload(self):
        app.add_book(self.library, "B001", "Python Basics", "A. Author")
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "data" / "books.json"
            with patch.object(app, "DATA_FILE", target):
                app.save_library(self.library)
                loaded = app.load_library()
            self.assertEqual(loaded, self.library)
            self.assertTrue(target.exists())

    def test_load_missing_file_creates_empty_library(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "data" / "books.json"
            with patch.object(app, "DATA_FILE", target):
                self.assertEqual(app.load_library(), {})
                self.assertTrue(target.exists())

    def test_load_invalid_json_returns_empty_library(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "books.json"
            target.write_text("{invalid json", encoding="utf-8")
            with patch.object(app, "DATA_FILE", target):
                self.assertEqual(app.load_library(), {})

    def test_login_success(self):
        with patch("builtins.input", side_effect=["admin", "admin123"]):
            self.assertTrue(app.login())

    def test_login_stops_after_three_failed_attempts(self):
        with patch("builtins.input", side_effect=["wrong", "bad", "wrong", "bad", "wrong", "bad"]):
            self.assertFalse(app.login())


if __name__ == "__main__":
    unittest.main(verbosity=2)
