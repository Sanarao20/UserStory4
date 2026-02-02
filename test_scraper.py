import os
import csv
import unittest
import logging
from unittest.mock import patch
from scraper import scrape_books, save_to_csv, OUTPUT_FILE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler("test_scraper_mock.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

MOCK_BOOKS = [
    {
        "Title": "Test Book 1",
        "Price": "£10.99",
        "Rating": 3,
        "Availability": "In stock",
        "Product URL": "https://books.toscrape.com/catalogue/test-book-1/index.html"
    },
    {
        "Title": "Test Book 2",
        "Price": "£15.50",
        "Rating": 4,
        "Availability": "Out of stock",
        "Product URL": "https://books.toscrape.com/catalogue/test-book-2/index.html"
    }
]

def mock_scrape_books():
    return MOCK_BOOKS

class TestBookScraperMocked(unittest.TestCase):

    @patch("scraper.scrape_books", side_effect=mock_scrape_books)
    def test_csv_file_download(self, mock_method):
        "Test case 1: verify CSV file download"
        logger.info("Running test: CSV file download")
        data = mock_scrape_books()
        save_to_csv(data)
        self.assertTrue(os.path.exists(OUTPUT_FILE))
        logger.info(f"CSV file '{OUTPUT_FILE}' exists.")

    @patch("scraper.scrape_books", side_effect=mock_scrape_books)
    def test_csv_file_extraction(self, mock_method):
        "Test case 2: verify CSV can be read"
        logger.info("Running test: CSV file extraction")
        data = mock_scrape_books()
        save_to_csv(data)
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertGreater(len(rows), 1)
        logger.info(f"CSV file '{OUTPUT_FILE}' has {len(rows)-1} data rows.")

    @patch("scraper.scrape_books", side_effect=mock_scrape_books)
    def test_csv_file_format(self, mock_method):
        "Test case 3: validate file type and format"
        logger.info("Running test: CSV file format")
        data = mock_scrape_books()
        save_to_csv(data)
        self.assertTrue(OUTPUT_FILE.endswith(".csv"))
        logger.info(f"CSV file '{OUTPUT_FILE}' format validated.")

    @patch("scraper.scrape_books", side_effect=mock_scrape_books)
    def test_csv_data_structure(self, mock_method):
        "Test case 4: validate CSV header structure"
        logger.info("Running test: CSV data structure")
        data = mock_scrape_books()
        save_to_csv(data)
        expected_header = ["Title", "Price", "Rating", "Availability", "Product URL"]
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(header, expected_header)
        logger.info("CSV header structure validated successfully.")

    @patch("scraper.scrape_books", side_effect=mock_scrape_books)
    def test_missing_or_invalid_data(self, mock_method):
        "Test case 5: ensure no missing or invalid data"
        logger.info("Running test: Missing or invalid data")
        data = mock_scrape_books()
        save_to_csv(data)
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, start=1):
                self.assertTrue(row["Title"], f"Missing Title at row {idx}")
                self.assertTrue(row["Price"], f"Missing Price at row {idx}")
                self.assertIn(row["Availability"], ["In stock", "Out of stock"], f"Invalid Availability at row {idx}")
                self.assertTrue(row["Product URL"], f"Missing Product URL at row {idx}")
                self.assertTrue(str(row["Rating"]).isdigit(), f"Invalid Rating at row {idx}")
        logger.info("All rows validated for missing or invalid data.")

if __name__ == "__main__":
    unittest.main()
