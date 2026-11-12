import unittest
from unittest.mock import patch

from src.db_loader import load_complaints


class TestDbLoader(unittest.TestCase):

    @patch("src.db_loader.psycopg.connect")
    def test_existing_and_invalid_records(self, mock_connect):

        # Create a fake database cursor
        mock_cursor = (
            mock_connect.return_value
            .__enter__.return_value
            .cursor.return_value
            .__enter__.return_value
        )

        # Simulate an existing record
        mock_cursor.rowcount = 0

        rows = [
            {
                "odi_number": "   ",
                "make": "audi",
                "model": "a5",
                "model_year": 2018,
                "component": "ENGINE",
                "date_filed": "2018-01-01",
                "summary": "Example complaint"
            },
            {
                "odi_number": "12345",
                "make": "audi",
                "model": "a5",
                "model_year": 2018,
                "component": "ELECTRICAL SYSTEM",
                "date_filed": "2018-02-01",
                "summary": "Example complaint"
            }
        ]

        result = load_complaints(
            rows,
            password="test_password"
        )

        self.assertEqual(result, (0, 1, 1))
        mock_cursor.execute.assert_called_once()


    @patch("src.db_loader.psycopg.connect")
    def test_new_record_is_inserted(self, mock_connect):

        mock_cursor = (
            mock_connect.return_value
            .__enter__.return_value
            .cursor.return_value
            .__enter__.return_value
        )

        # Simulate a successful database INSERT
        mock_cursor.rowcount = 1

        rows = [
            {
                "odi_number": "999999",
                "make": "audi",
                "model": "a5",
                "model_year": 2018,
                "component": "ENGINE",
                "date_filed": "2018-05-10",
                "summary": "Test complaint"
            }
        ]

        result = load_complaints(
            rows,
            password="test_password"
        )

        self.assertEqual(result, (1, 0, 0))
        mock_cursor.execute.assert_called_once()



if __name__ == "__main__":
    unittest.main()
