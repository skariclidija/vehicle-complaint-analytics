import unittest

from src.data_quality import (
    check_data_quality,
    remove_invalid_and_duplicate_rows
)

class TestDataQuality(unittest.TestCase):

    def test_missing_and_duplicate_ids(self):

        rows = [
            {"odi_number": "100"},
            {"odi_number": "200"},
            {"odi_number": "100 "},
            {"odi_number": "   "},
            {"odi_number": "300"}
        ]

        result = check_data_quality(rows)

        self.assertEqual(result["total_records"], 5)
        self.assertEqual(result["missing_ids"], 1)
        self.assertEqual(result["duplicate_ids"], 1)

    def test_remove_invalid_and_duplicate_rows(self):

        rows = [
            {"odi_number": "100"},
            {"odi_number": "200"},
            {"odi_number": "100 "},
            {"odi_number": ""},
            {"odi_number": "300"}
        ]

        cleaned = remove_invalid_and_duplicate_rows(rows)

        self.assertEqual(len(cleaned), 3)

        self.assertEqual(
            [row["odi_number"] for row in cleaned],
            ["100", "200", "300"]
        )

        self.assertEqual(len(rows), 5)
    def test_remove_invalid_and_duplicate_rows(self):

        rows = [
            {"odi_number": "100"},
            {"odi_number": "200"},
            {"odi_number": "100 "},
            {"odi_number": ""},
            {"odi_number": "300"}
        ]

        cleaned = remove_invalid_and_duplicate_rows(rows)

        self.assertEqual(len(cleaned), 3)

        self.assertEqual(
            [row["odi_number"] for row in cleaned],
            ["100", "200", "300"]
        )

        self.assertEqual(len(rows), 5)

if __name__ == "__main__":
    unittest.main()
