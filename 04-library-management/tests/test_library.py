import unittest
from library_management import add_book, issue_book, modify_book, return_book


class LibraryManagementTests(unittest.TestCase):
    def setUp(self):
        self.library = {}

    def test_add_book(self):
        self.assertTrue(add_book(self.library, "b001", "Python Basics", "A. Author"))
        self.assertEqual(self.library["B001"]["title"], "Python Basics")

    def test_reject_duplicate_id_and_title(self):
        add_book(self.library, "B001", "Python Basics", "A. Author")
        self.assertFalse(add_book(self.library, "B001", "Another Book", "B. Author"))
        self.assertFalse(add_book(self.library, "B002", "python basics", "B. Author"))

    def test_issue_and_return_book(self):
        add_book(self.library, "B001", "Python Basics", "A. Author")
        self.assertTrue(issue_book(self.library, "B001", "Ankush"))
        self.assertFalse(issue_book(self.library, "B001", "Another Borrower"))
        self.assertEqual(self.library["B001"]["issued_to"], "Ankush")
        self.assertTrue(return_book(self.library, "B001"))
        self.assertTrue(self.library["B001"]["available"])
        self.assertIsNone(self.library["B001"]["issued_to"])

    def test_modify_book(self):
        add_book(self.library, "B001", "Python Basics", "A. Author")
        self.assertTrue(modify_book(self.library, "B001", "Python for Beginners", "A. Author"))
        self.assertEqual(self.library["B001"]["title"], "Python for Beginners")


if __name__ == "__main__":
    unittest.main()
