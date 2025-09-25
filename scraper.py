
import sqlite3
import json
from datetime import datetime, timedelta
import time
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- Configuration ---
DB_FILE = 'reviews_cache.db'
CACHE_EXPIRY_DAYS = 7  # How long to keep results in cache

# --- Database Functions ---

def init_db():
    """Initializes the SQLite database and creates tables if they don't exist."""
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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    price REAL NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            ''')
            conn.commit()
            print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")

def _get_cached_data(url: str) -> dict | None:
    """
    Retrieves cached reviews and full price history for a URL.
    Reviews are only returned if they are not older than CACHE_EXPIRY_DAYS.
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get cached reviews
            cursor.execute("SELECT reviews_json, timestamp FROM reviews WHERE url = ?", (url,))
            review_row = cursor.fetchone()
            reviews = None
            if review_row:
                timestamp = datetime.fromisoformat(review_row['timestamp'])
                if datetime.now() - timestamp < timedelta(days=CACHE_EXPIRY_DAYS):
                    print(f"Cache hit for reviews: {url}")
                    reviews = json.loads(review_row['reviews_json'])
                else:
                    print(f"Cache expired for reviews: {url}")

            # Get price history
            cursor.execute("SELECT price, timestamp FROM price_history WHERE url = ? ORDER BY timestamp ASC", (url,))
            price_history = [{"price": row['price'], "timestamp": row['timestamp']} for row in cursor.fetchall()]

            if reviews is not None or price_history:
                return {"reviews": reviews, "price_history": price_history}

    except (sqlite3.Error, FileNotFoundError):
        pass  # If DB doesn't exist or there's an error, proceed to scrape
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
        print(f"Database write error for reviews: {e}")

def _cache_price(url: str, price: float):
    """Saves a new price entry to the price_history table."""
    if price is None:
        return
    timestamp = datetime.now().isoformat()
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO price_history (url, price, timestamp) VALUES (?, ?, ?)",
                (url, price, timestamp)
            )
            conn.commit()
            print(f"Successfully cached price {price} for URL: {url}")
    except sqlite3.Error as e:
        print(f"Database write error for price: {e}")

# --- Scraping Logic ---

def _scrape_with_playwright(url: str) -> dict | None:
    """
    Scrapes reviews, price, title, and description from a given URL using Playwright.
    Returns a dictionary containing 'reviews', 'price', 'title', and 'description'.
    """
    print(f"Scraping data from: {url} using Playwright...")

    FLIPKART_REVIEW_XPATHS = [
        "//div[contains(@class, 't-ZTKy') or contains(@class, '_6K-7Co')]",
        "//*[text()='Ratings & Reviews']/../..//div[contains(@class, 'ZmyHeo')]",
        "//div[div[contains(., 'Certified Buyer')]]/div[1]"
    ]
    AMAZON_REVIEW_XPATHS = [
<<<<<<< HEAD
        "//span[@data-hook='review-body']//span[not(@class)]",
        "//div[contains(@class, 'review-text-content')]/span",
=======
        "//div[contains(@class, 'review-text-content')]/span",
        "//span[@data-hook='review-body']//span",
>>>>>>> e9414c5600577b26d2ed2f3aaecc1bee4790b887
        "//div[@data-hook='review-collapsed']//span",
        "//span[contains(@class, 'cr-original-review-text')]",
        "//div[contains(@class, 'cr-original-review-text')]",
        "//div[contains(@data-hook, 'review-body')]//span",
        "//span[contains(@class, 'review-text')]",
        "//div[contains(@class, 'reviewText')]/span",
        "//div[@data-hook='review-body']/span",
        "//span[@data-hook='review-body']",
        "//div[contains(@class, 'a-expander-content')]/span",
        "//span[contains(text(), 'review') or contains(text(), 'product') or contains(text(), 'good') or contains(text(), 'bad')]"
    ]
    
    FLIPKART_PRICE_XPATH = "//div[contains(@class, '_30jeq3')]"
    AMAZON_PRICE_XPATH = "//span[contains(@class, 'a-price-whole')] | //span[contains(@class, 'a-price-current')] | //span[@class='a-offscreen']"

    # Product title selectors
    FLIPKART_TITLE_XPATHS = [
        "//span[contains(@class,'B_NuCI')]",
        "//h1[contains(@class,'yhB1nd')]",
        "//span[contains(@class,'VU-ZEz')]",
    ]
    AMAZON_TITLE_XPATHS = [
        "//span[@id='productTitle']",
        "//h1[@id='title']",
        "//h1[contains(@class,'a-size-large')]",
    ]

    # Product description/ highlights selectors
    FLIPKART_DESC_XPATHS = [
        "//div[text()='Description']/following::div[1]",
        "//div[contains(@class,'_1AN87F')]/div",
        "//div[contains(@class,'_1mXcCf')]",
        "//div[contains(@class,'_2418kt')]",
        "//div[@id='productDescription']//p",
        "//div[text()='Highlights']/following::ul[1]",
    ]
    AMAZON_DESC_XPATHS = [
        "//div[@id='feature-bullets']",
        "//div[@id='productDescription']",
    ]
    
    FLIPKART_PRICE_XPATH = "//div[contains(@class, '_30jeq3')]"
    AMAZON_PRICE_XPATH = "//span[contains(@class, 'a-price-whole')]"

    # Product title selectors
    FLIPKART_TITLE_XPATHS = [
        "//span[contains(@class,'B_NuCI')]",
        "//h1[contains(@class,'yhB1nd')]",
    ]
    AMAZON_TITLE_XPATHS = [
        "//span[@id='productTitle']",
    ]

    # Product description/ highlights selectors
    FLIPKART_DESC_XPATHS = [
        "//div[text()='Description']/following::div[1]",
        "//div[contains(@class,'_1AN87F')]/div",
        "//div[contains(@class,'_1mXcCf')]",
        "//div[contains(@class,'_2418kt')]",
        "//div[@id='productDescription']//p",
        "//div[text()='Highlights']/following::ul[1]",
    ]
    AMAZON_DESC_XPATHS = [
        "//div[@id='feature-bullets']",
        "//div[@id='productDescription']",
    ]

    if 'flipkart.com' in url:
        review_xpaths = FLIPKART_REVIEW_XPATHS
        price_xpath = FLIPKART_PRICE_XPATH
        title_xpaths = FLIPKART_TITLE_XPATHS
        desc_xpaths = FLIPKART_DESC_XPATHS
    elif 'amazon' in url:
        review_xpaths = AMAZON_REVIEW_XPATHS
        price_xpath = AMAZON_PRICE_XPATH
        title_xpaths = AMAZON_TITLE_XPATHS
        desc_xpaths = AMAZON_DESC_XPATHS
    else:
        print("Warning: URL is not for Flipkart or Amazon. Using generic selectors.")
        review_xpaths = ["//div[contains(@class, 'review-text')]"]
        price_xpath = None
        title_xpaths = ["//h1"]
        desc_xpaths = ["//div[contains(.,'Description')]"]

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
<<<<<<< HEAD
            
            # Set user agent to avoid detection
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })
            
            # Set shorter timeout for Amazon to prevent hanging
            timeout = 20000 if 'amazon' in url else 60000
            print(f"Loading page with {timeout/1000}s timeout...")
            page.goto(url, wait_until='domcontentloaded', timeout=timeout)
            
            # Scroll to load dynamic content
            scroll_count = 2 if 'amazon' in url else 3  # Less scrolling for Amazon
            for i in range(scroll_count):
=======
            page.goto(url, wait_until='domcontentloaded', timeout=60000)

            for _ in range(5):
>>>>>>> e9414c5600577b26d2ed2f3aaecc1bee4790b887
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.3)  # Shorter delay

            # Scrape title
            title = None
            for xp in title_xpaths:
<<<<<<< HEAD
                try:
                    el = page.query_selector(xp)
                    if el:
                        t = (el.inner_text() or '').strip()
                        if t:
                            title = t
                            break
                except Exception:
=======
                try:
                    el = page.query_selector(xp)
                    if el:
                        t = (el.inner_text() or '').strip()
                        if t:
                            title = t
                            break
                except Exception:
                    continue

            # Scrape description/highlights (concatenate visible blocks)
            description = None
            for xp in desc_xpaths:
                try:
                    els = page.query_selector_all(xp)
                    if els:
                        texts = []
                        for el in els:
                            try:
                                txt = el.inner_text().strip()
                                if txt:
                                    texts.append(txt)
                            except Exception:
                                continue
                        if texts:
                            # Deduplicate lines and trim
                            seen = set()
                            deduped = []
                            for line in texts:
                                if line not in seen:
                                    seen.add(line)
                                    deduped.append(line)
                            description = " \n ".join(deduped)[:2000]
                            break
                except Exception:
                    continue

            # Scrape reviews
            reviews = []
            for i, xpath in enumerate(review_xpaths):
                try:
                    page.wait_for_selector(xpath, timeout=5000)
                    elements = page.query_selector_all(xpath)
                    if elements:
                        reviews = [el.inner_text() for el in elements if el.inner_text().strip()]
                        if reviews:
                            print(f"Success! Found {len(reviews)} reviews with selector #{i+1}.")
                            break
                except PlaywrightTimeoutError:
                    print(f"Review selector #{i+1} did not find any elements.")
>>>>>>> e9414c5600577b26d2ed2f3aaecc1bee4790b887
                    continue
            
            # Scrape price
            price = None
            if price_xpath:
                try:
                    price_element = page.query_selector(price_xpath)
                    if price_element:
                        price_text = price_element.inner_text()
                        # Clean price text (e.g., "₹1,29,999" -> 129999.0)
                        price_digits = re.sub(r'[^\d.]', '', price_text)
                        if price_digits:
                            price = float(price_digits)
                            print(f"Success! Found price: {price}")
                except Exception as e:
                    print(f"Could not extract price: {e}")

            # Scrape description/highlights (concatenate visible blocks)
            description = None
            for xp in desc_xpaths:
                try:
                    els = page.query_selector_all(xp)
                    if els:
                        texts = []
                        for el in els:
                            try:
                                txt = el.inner_text().strip()
                                if txt:
                                    texts.append(txt)
                            except Exception:
                                continue
                        if texts:
                            # Deduplicate lines and trim
                            seen = set()
                            deduped = []
                            for line in texts:
                                if line not in seen:
                                    seen.add(line)
                                    deduped.append(line)
                            description = " \n ".join(deduped)[:2000]
                            break
                except Exception:
                    continue

            # Scrape reviews with shorter timeout for Amazon
            reviews = []
            review_timeout = 3000 if 'amazon' in url else 5000
            
            # Special handling for Amazon - try to navigate to reviews section first
            if 'amazon' in url:
                try:
                    # Try to find and click "See all reviews" or scroll to reviews section
                    see_all_reviews = page.query_selector("[data-hook='see-all-reviews-link-foot']") or \
                                    page.query_selector("a[href*='#customerReviews']") or \
                                    page.query_selector("a[href*='/product-reviews/']") or \
                                    page.query_selector("[data-hook='reviews-block']")
                    
                    if see_all_reviews:
                        print("Found reviews section, scrolling...")
                        page.evaluate("document.querySelector('[data-hook=\"reviews-block\"]')?.scrollIntoView()")
                        time.sleep(1)
                except Exception as e:
                    print(f"Could not navigate to reviews section: {e}")
            
            for i, xpath in enumerate(review_xpaths):
                try:
                    page.wait_for_selector(xpath, timeout=review_timeout)
                    elements = page.query_selector_all(xpath)
                    if elements:
                        potential_reviews = []
                        for el in elements:
                            text = el.inner_text().strip() if el.inner_text() else ''
                            # Filter out very short texts and non-review content
                            if len(text) > 20 and not any(skip in text.lower() for skip in ['helpful', 'report', 'verified purchase', 'customer images']):
                                potential_reviews.append(text)
                        
                        if potential_reviews:
                            reviews = potential_reviews
                            print(f"Success! Found {len(reviews)} reviews with selector #{i+1}.")
                            break
                except PlaywrightTimeoutError:
                    print(f"Review selector #{i+1} did not find any elements.")
                    continue
                except Exception as e:
                    print(f"Error with selector #{i+1}: {e}")
                    continue
            
            # If no reviews found with XPath, try a different approach for Amazon
            if not reviews and 'amazon' in url:
                try:
                    print("Trying alternative Amazon review extraction...")
                    # Look for any text content that looks like reviews
                    all_text_elements = page.query_selector_all("span, div, p")
                    potential_reviews = []
                    
                    for element in all_text_elements[:100]:  # Limit to first 100 elements
                        try:
                            text = element.inner_text().strip()
                            # Look for review-like content
                            if (len(text) > 30 and len(text) < 500 and 
                                any(word in text.lower() for word in ['product', 'good', 'bad', 'excellent', 'poor', 'love', 'hate', 'recommend', 'quality']) and
                                not any(skip in text.lower() for skip in ['price', 'cart', 'buy now', 'add to', 'seller', 'shipping'])):
                                potential_reviews.append(text)
                                if len(potential_reviews) >= 10:
                                    break
                        except:
                            continue
                    
                    if potential_reviews:
                        reviews = potential_reviews
                        print(f"Alternative method found {len(reviews)} potential reviews.")
                except Exception as e:
                    print(f"Alternative extraction failed: {e}")
            
            # Scrape price
            price = None
            if price_xpath:
                try:
                    price_element = page.query_selector(price_xpath)
                    if price_element:
                        price_text = price_element.inner_text()
                        # Clean price text (e.g., "₹1,29,999" -> 129999.0)
                        price_digits = re.sub(r'[^\d.]', '', price_text)
                        if price_digits:
                            price = float(price_digits)
                            print(f"Success! Found price: {price}")
                except Exception as e:
                    print(f"Could not extract price: {e}")

            browser.close()
            return {"reviews": reviews, "price": price, "title": title, "description": description}

        except PlaywrightTimeoutError:
            print(f"Error: Timed out loading page {url}.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred with Playwright: {e}")
            return None

# --- Main Public Function ---

def scrape_data(url: str) -> dict | None:
    """
    Main function to get reviews and price for a URL, using a cache-first approach.
    Always scrapes for the latest price, but uses cached reviews if available.
    """
    init_db() # Ensure DB is ready
    
    cached_data = _get_cached_data(url)
    
    # Use cached reviews if available and not expired
    if cached_data and cached_data.get('reviews'):
        reviews = cached_data['reviews']
<<<<<<< HEAD
        print(f"Using cached reviews: {len(reviews)} reviews")
    else:
        reviews = None # Needs scraping

    try:
        # Always scrape the page to get the latest price and fresh reviews if needed
        scraped_data = _scrape_with_playwright(url)
    except Exception as scrape_error:
        print(f"Scraping failed with error: {scrape_error}")
        scraped_data = None

    if scraped_data is None:
        print("Scraping failed, checking cached data...")
        # If scraping fails, return cached data if it exists, otherwise fail
        if cached_data and (cached_data.get('price_history') or cached_data.get('reviews')):
            print("Returning cached data due to scraping failure")
            return cached_data
        else:
            print("No cached data available, scraping completely failed")
            return None
=======
    else:
        reviews = None # Needs scraping

    # Always scrape the page to get the latest price and fresh reviews if needed
    scraped_data = _scrape_with_playwright(url)

    if scraped_data is None:
        # If scraping fails, return cached data if it exists, otherwise fail
        return cached_data if cached_data and cached_data.get('price_history') else None
>>>>>>> e9414c5600577b26d2ed2f3aaecc1bee4790b887

    # Use scraped reviews only if we didn't have valid cached ones
    if reviews is None:
        reviews = scraped_data.get('reviews', [])
        if reviews:
<<<<<<< HEAD
            print(f"Caching {len(reviews)} newly scraped reviews")
            _cache_reviews(url, reviews)
        else:
            print("No reviews found in scraped data")
=======
            _cache_reviews(url, reviews)
>>>>>>> e9414c5600577b26d2ed2f3aaecc1bee4790b887

    # Always cache the newly scraped price
    if 'price' in scraped_data and scraped_data['price'] is not None:
        _cache_price(url, scraped_data['price'])
<<<<<<< HEAD
        print(f"Cached new price: {scraped_data['price']}")
=======
>>>>>>> e9414c5600577b26d2ed2f3aaecc1bee4790b887

    # Get updated price history
    updated_cached_data = _get_cached_data(url)
    price_history = updated_cached_data.get('price_history', []) if updated_cached_data else []

    # Pass through non-cached fields from latest scrape
    title = scraped_data.get('title')
    description = scraped_data.get('description')
<<<<<<< HEAD
    
    result = {
        "reviews": reviews, 
        "price_history": price_history, 
        "title": title, 
        "description": description
    }
    
    print(f"Final result: {len(reviews)} reviews, title: {title[:30] if title else 'None'}...")
    return result
=======

    return {"reviews": reviews, "price_history": price_history, "title": title, "description": description}
>>>>>>> e9414c5600577b26d2ed2f3aaecc1bee4790b887


# --- Example for direct testing ---
if __name__ == '__main__':
    test_url = 'https://www.flipkart.com/google-pixel-7a-sea-128-gb/p/itm8577377a36c72'
    
    print("--- Running Scraper Test ---")
    data = scrape_data(test_url)

    if data:
        print(f"\nSuccessfully retrieved {len(data.get('reviews', []))} reviews.")
        if data.get('price_history'):
            print(f"Latest price: {data['price_history'][-1]['price']}")
            print(f"Price history has {len(data['price_history'])} entries.")
        
        print("\n--- Testing Cache ---")
        # This second call should be faster
        scrape_data(test_url)
    else:
        print("\nFailed to retrieve data for the test URL.")
