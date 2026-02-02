import requests
import csv
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.exceptions import RequestException

BASE_URL = "https://books.toscrape.com/"
OUTPUT_FILE = "books_data.csv"
TIMEOUT = 10

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

RATING_MAP = {
    "One": 1,"Two": 2,"Three": 3,"Four": 4,"Five": 5
}

def fetch_page(url):
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        response.encoding=response.apparent_encoding
        return response.text
    except RequestException as e:
        logger.error(f"HTTP error while fetching {url} | {e}")
        return None


def parse_book(book):
    try:
        title = book.h3.a.get("title")
        price = book.select_one(".price_color").text.strip()
        raw_availability = book.select_one(".availability").text.lower()
        availability = "In stock" if "in stock" in raw_availability else "Out of stock"

        rating_class = book.select_one(".star-rating")["class"][1]
        rating = RATING_MAP.get(rating_class)

        product_url = urljoin(BASE_URL, book.h3.a["href"])

        if not all([title, price, rating, availability, product_url]):
            raise ValueError("Missing required field")

        return {
            "Title": title,
            "Price": price,
            "Rating": rating,
            "Availability": availability,
            "Product URL": product_url
        }

    except Exception as e:
        logger.warning(f"Skipping book due to parsing error | {e}")
        return None


def save_to_csv(data):
    try:
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["Title", "Price", "Rating", "Availability", "Product URL"]
            )
            writer.writeheader()
            writer.writerows(data)

        logger.info(f"Saved {len(data)} records to {OUTPUT_FILE}")

    except Exception as e:
        logger.error(f"Failed to write CSV | {e}")

def scrape_books():
    all_books = []
    page_url = BASE_URL
    page_count = 1

    while page_url:
        logger.info(f"Scraping page {page_count}: {page_url}")

        html = fetch_page(page_url)
        if not html:
            logger.warning("Stopping scraper due to page fetch failure")
            break

        soup = BeautifulSoup(html, "html.parser")
        books = soup.select(".product_pod")

        for book in books:
            book_data = parse_book(book)
            if book_data:
                all_books.append(book_data)

        # Pagination with protection
        try:
            next_page = soup.select_one("li.next a")
            if next_page:
                page_url = urljoin(page_url, next_page["href"])
                page_count += 1
            else:
                page_url = None
        except Exception as e:
            logger.error(f"Pagination error | {e}")
            break

    return all_books

if __name__ == "__main__":
    logger.info("Book scraping started")
    books = scrape_books()
    save_to_csv(books)
    logger.info("Book scraping completed")
