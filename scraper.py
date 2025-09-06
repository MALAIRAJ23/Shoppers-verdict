'''
Scraper module for Shoppers-Verdict.

This version uses Playwright for robust browser automation and an SQLite database
to cache results, improving performance and reducing redundant scrapes.
'''

import sqlite3
import json
from datetime import datetime, timedelta
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- Configuration ---
DB_FILE = 'reviews_cache.db'
CACHE_EXPIRY_DAYS = 7  # How long to keep results in cache

# --- Database Functions ---

def init_db():
    """Initializes the SQLite database and creates the reviews table if it doesn't exist."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    url TEXT PRIMARY KEY,
                    reviews_json TEXT NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            ''')
            conn.commit()
            print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")

def _get_cached_reviews(url: str) -> list[str] | None:
    """
    Retrieves cached reviews for a URL if they are not older than CACHE_EXPIRY_DAYS.
    Returns a list of reviews or None if not found or expired.
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT reviews_json, timestamp FROM reviews WHERE url = ?", (url,))
            row = cursor.fetchone()
            if row:
                reviews_json, timestamp_str = row
                timestamp = datetime.fromisoformat(timestamp_str)
                if datetime.now() - timestamp < timedelta(days=CACHE_EXPIRY_DAYS):
                    print(f"Cache hit for URL: {url}")
                    return json.loads(reviews_json)
                else:
                    print(f"Cache expired for URL: {url}")
    except (sqlite3.Error, FileNotFoundError):
        # If DB doesn't exist or there's an error, proceed to scrape
        pass
    return None

def _cache_reviews(url: str, reviews: list[str]):
    """Saves scraped reviews to the SQLite database."""
    reviews_json = json.dumps(reviews)
    timestamp = datetime.now().isoformat()
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO reviews (url, reviews_json, timestamp) VALUES (?, ?, ?)",
                (url, reviews_json, timestamp)
            )
            conn.commit()
            print(f"Successfully cached {len(reviews)} reviews for URL: {url}")
    except sqlite3.Error as e:
        print(f"Database write error: {e}")

# --- Scraping Logic ---

def _scrape_with_playwright(url: str) -> list[str] | None:
    """
    Scrapes reviews from a given URL using Playwright and robust XPath selectors.
    """
    print(f"Scraping reviews from: {url} using Playwright...")

    # --- Robust XPath Selectors (tried in order) ---
    # Using contains() and text() makes these less likely to break with minor class changes.
    FLIPKART_XPATHS = [
        "//div[contains(@class, 't-ZTKy') or contains(@class, '_6K-7Co')]",
        "//*[text()='Ratings & Reviews']/../..//div[contains(@class, 'ZmyHeo')]",
        "//div[div[contains(., 'Certified Buyer')]]/div[1]"
    ]
    AMAZON_XPATHS = [
        "//span[@data-hook='review-body']//span",
        "//div[@data-hook='review-collapsed']//span",
    ]

    if 'flipkart.com' in url:
        xpaths_to_try = FLIPKART_XPATHS
    elif 'amazon' in url:
        xpaths_to_try = AMAZON_XPATHS
    else:
        print(f"Warning: URL is not for Flipkart or Amazon. Using generic selectors.")
        xpaths_to_try = ["//div[contains(@class, 'review-text')]"]

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until='domcontentloaded', timeout=60000)

            # Scroll multiple times to ensure all lazy-loaded content is triggered
            for _ in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

            reviews = []
            for i, xpath in enumerate(xpaths_to_try):
                try:
                    page.wait_for_selector(xpath, timeout=5000)
                    elements = page.query_selector_all(xpath)
                    if elements:
                        reviews = [el.inner_text() for el in elements if el.inner_text().strip()]
                        if reviews:
                            print(f"Success! Found {len(reviews)} reviews with selector #{i+1}.")
                            break  # Exit loop if reviews are found
                except PlaywrightTimeoutError:
                    print(f"Selector #{i+1} did not find any elements.")
                    continue

            browser.close()
            return reviews if reviews else []

        except PlaywrightTimeoutError:
            print(f"Error: Timed out loading page {url}.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred with Playwright: {e}")
            return None

# --- Main Public Function ---

def scrape_reviews(url: str) -> list[str] | None:
    """
    Main function to get reviews for a URL, using a cache-first approach.

    Returns:
        A list of review strings, an empty list if no reviews are found,
        or None if a critical scraping error occurred.
    """
    init_db() # Ensure DB is ready
    cached_reviews = _get_cached_reviews(url)
    if cached_reviews is not None:
        return cached_reviews

    scraped_reviews = _scrape_with_playwright(url)

    if scraped_reviews is not None:
        _cache_reviews(url, scraped_reviews)
    
    return scraped_reviews

# --- Example for direct testing ---
if __name__ == '__main__':
    test_url = 'https://www.flipkart.com/google-pixel-7a-sea-128-gb/p/itm8577377a36c72'
    
    print("--- Running Scraper Test ---")
    reviews_list = scrape_reviews(test_url)

    if reviews_list is not None:
        print(f"\nSuccessfully retrieved {len(reviews_list)} reviews for the test URL.")
        print("First 5 reviews:")
        for i, review in enumerate(reviews_list[:5]):
            print(f"{i+1}: {review[:100]}...")
        
        print("\n--- Testing Cache ---")
        # This second call should be much faster and hit the cache.
        scrape_reviews(test_url)
    else:
        print("\nFailed to retrieve reviews for the test URL.")