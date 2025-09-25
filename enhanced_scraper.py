import asyncio
import random
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import time
from urllib.parse import urlparse, parse_qs
import re
from typing import List, Dict, Optional
import logging
import json
import sqlite3
from datetime import datetime, timedelta

# --- Configuration ---
DB_FILE = 'reviews_cache.db'
CACHE_EXPIRY_DAYS = 7

# Enhanced Amazon review selectors
AMAZON_REVIEW_XPATHS = [
    "//span[@data-hook='review-body']//span[not(@class)]",
    "//div[contains(@class, 'review-text-content')]/span",
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

def scrape_amazon_mobile_fallback(url: str, max_reviews: int = 10) -> Dict:
    """Fallback method using requests and BeautifulSoup for Amazon mobile site"""
    print(f"Trying Amazon mobile fallback for: {url}")
    
    try:
        # Convert to mobile URL
        mobile_url = url.replace('www.amazon.', 'm.amazon.')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        session = requests.Session()
        response = session.get(mobile_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = None
            title_selectors = ['#productTitle', '.product-title', 'h1', '[data-automation-id="product-title"]']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    break
            
            # Extract reviews from mobile site
            reviews = []
            review_selectors = [
                '[data-hook="review-body"] span',
                '.review-text',
                '.cr-original-review-text',
                '[data-hook="review-collapsed"] span',
                '.reviewText'
            ]
            
            for selector in review_selectors:
                review_elements = soup.select(selector)
                if review_elements:
                    for elem in review_elements[:max_reviews]:
                        review_text = elem.get_text().strip()
                        if len(review_text) > 15:
                            reviews.append(review_text)
                    if reviews:
                        break
            
            # If no structured reviews, try content-based search
            if not reviews:
                print("Trying content-based Amazon review extraction...")
                all_spans = soup.find_all(['span', 'div', 'p'])
                for element in all_spans[:200]:
                    text = element.get_text().strip()
                    if (30 < len(text) < 500 and 
                        any(word in text.lower() for word in ['product', 'good', 'bad', 'excellent', 'poor', 'love', 'hate', 'recommend', 'quality', 'works', 'buy', 'purchase']) and
                        not any(skip in text.lower() for skip in ['price', 'cart', 'buy now', 'add to', 'seller', 'shipping', 'delivery', 'return'])):
                        reviews.append(text)
                        if len(reviews) >= max_reviews:
                            break
            
            print(f"Mobile fallback found {len(reviews)} reviews, title: {title}")
            return {
                'reviews': reviews,
                'title': title,
                'price': None,
                'description': None,
                'source': 'amazon_mobile'
            }
    
    except Exception as e:
        print(f"Mobile fallback error: {e}")
    
    return {'reviews': [], 'title': None, 'price': None, 'description': None, 'source': 'amazon_mobile', 'error': 'failed'}

async def scrape_amazon_reviews_enhanced(url: str, max_reviews: int = 10) -> Dict:
    """Enhanced Amazon scraping with multiple methods and fallbacks"""
    print(f"Enhanced Amazon scraping from: {url}")
    
    # Method 1: Try mobile scraping first (often works better)
    mobile_result = scrape_amazon_mobile_fallback(url, max_reviews)
    if mobile_result.get('reviews'):
        print("Mobile scraping successful!")
        return mobile_result
    
    # Method 2: Try Playwright with enhanced stealth
    async with async_playwright() as p:
        try:
            # Launch browser with maximum stealth settings
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=site-per-process',
                    '--window-size=1920,1080'
                ]
            )
            
            # Rotate user agents
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
            ]
            
            context = await browser.new_context(
                user_agent=random.choice(user_agents),
                viewport={'width': 1920, 'height': 1080},
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none'
                }
            )
            
            # Add stealth script
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                window.chrome = {
                    runtime: {},
                };
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
            """)
            
            page = await context.new_page()
            page.set_default_timeout(25000)
            
            print(f"Navigating to: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=25000)
            
            # Add random delay
            await asyncio.sleep(random.uniform(2, 4))
            
            # Try to get product title first
            title = None
            title_selectors = [
                "#productTitle",
                "h1.a-size-large",
                "h1#title",
                ".product-title",
                "[data-automation-id='product-title']",
                "h1.a-size-base-plus"
            ]
            
            for selector in title_selectors:
                try:
                    title_element = await page.wait_for_selector(selector, timeout=3000)
                    if title_element:
                        title = await title_element.inner_text()
                        print(f"Found title with selector {selector}: {title[:50]}...")
                        break
                except:
                    continue
            
            # Scroll to reviews section
            try:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                await asyncio.sleep(1)
            except:
                pass
            
            # Try multiple review section approaches
            reviews = []
            
            # Method A: Try to find and click reviews section
            try:
                reviews_section_selectors = [
                    "a[data-hook='see-all-reviews-link-foot']",
                    "[data-hook='reviews-medley-footer'] a",
                    "a[href*='#reviews']",
                    "a[href*='customerReviews']"
                ]
                
                for selector in reviews_section_selectors:
                    try:
                        reviews_link = await page.query_selector(selector)
                        if reviews_link:
                            print(f"Found reviews link with selector: {selector}")
                            await reviews_link.click()
                            await page.wait_for_load_state("domcontentloaded")
                            await asyncio.sleep(2)
                            break
                    except:
                        continue
            except:
                pass
            
            # Method B: Try all enhanced XPath selectors
            enhanced_xpaths = AMAZON_REVIEW_XPATHS + [
                "//div[@data-hook='review']//span[contains(@class, 'review-text')]",
                "//div[contains(@class, 'review-item')]//span",
                "//span[contains(@class, 'cr-original-review-text')]",
                "//div[@data-testid='reviews-section']//span"
            ]
            
            for i, xpath in enumerate(enhanced_xpaths, 1):
                try:
                    print(f"Trying review selector #{i}: {xpath[:50]}...")
                    elements = await page.query_selector_all(f"xpath={xpath}")
                    
                    if elements:
                        print(f"Review selector #{i} found {len(elements)} elements")
                        for element in elements[:max_reviews]:
                            try:
                                review_text = await element.inner_text()
                                if review_text and len(review_text.strip()) > 15:
                                    clean_review = review_text.strip()
                                    if clean_review not in reviews:  # Avoid duplicates
                                        reviews.append(clean_review)
                                        print(f"Extracted review: {clean_review[:100]}...")
                            except:
                                continue
                        
                        if reviews:
                            print(f"Success! Found {len(reviews)} reviews with selector #{i}")
                            break
                    else:
                        print(f"Review selector #{i} did not find any elements")
                        
                except Exception as e:
                    print(f"Error with selector #{i}: {e}")
                    continue
            
            # Method C: Try CSS selectors as final fallback
            if not reviews:
                css_selectors = [
                    "[data-hook='review-body'] span:not([class])",
                    ".review-text",
                    ".cr-original-review-text",
                    "div[data-hook='review-collapsed'] span",
                    "[data-testid='review-text-content']",
                    ".reviewText"
                ]
                
                for selector in css_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            print(f"CSS selector '{selector}' found {len(elements)} elements")
                            for element in elements[:max_reviews]:
                                try:
                                    review_text = await element.inner_text()
                                    if review_text and len(review_text.strip()) > 15:
                                        clean_review = review_text.strip()
                                        if clean_review not in reviews:
                                            reviews.append(clean_review)
                                            print(f"CSS extracted review: {clean_review[:100]}...")
                                except:
                                    continue
                            if reviews:
                                break
                    except:
                        continue
            
            # Method D: Content-based extraction as last resort
            if not reviews:
                print("Trying content-based Amazon review extraction...")
                try:
                    all_elements = await page.query_selector_all("span, div, p")
                    for element in all_elements[:200]:
                        try:
                            text = await element.inner_text()
                            if text and (30 < len(text.strip()) < 500):
                                text = text.strip()
                                if (any(word in text.lower() for word in ['product', 'good', 'bad', 'excellent', 'poor', 'love', 'hate', 'recommend', 'quality', 'works', 'buy']) and
                                    not any(skip in text.lower() for skip in ['price', 'cart', 'buy now', 'add to', 'seller', 'shipping', 'delivery', 'return']) and
                                    text not in reviews):
                                    reviews.append(text)
                                    if len(reviews) >= max_reviews:
                                        break
                        except:
                            continue
                except Exception as e:
                    print(f"Content extraction error: {e}")
            
            # Extract price
            price = None
            price_selectors = [
                ".a-price-whole",
                ".a-price-current .a-offscreen",
                "[data-a-color='price'] .a-offscreen",
                ".a-price .a-offscreen"
            ]
            
            for selector in price_selectors:
                try:
                    price_element = await page.query_selector(selector)
                    if price_element:
                        price_text = await price_element.inner_text()
                        price_digits = re.sub(r'[^\d.]', '', price_text)
                        if price_digits:
                            price = float(price_digits)
                            break
                except:
                    continue
            
            # Extract description
            description = None
            desc_selectors = [
                "#feature-bullets ul",
                "#productDescription",
                "[data-feature-name='featurebullets']"
            ]
            
            for selector in desc_selectors:
                try:
                    desc_element = await page.query_selector(selector)
                    if desc_element:
                        description = await desc_element.inner_text()
                        if description:
                            description = description.strip()[:2000]
                            break
                except:
                    continue
            
            await browser.close()
            
            print(f"Final Playwright result: {len(reviews)} reviews, title: {title}")
            return {
                'reviews': reviews,
                'title': title,
                'price': price,
                'description': description,
                'source': 'amazon_playwright'
            }
            
        except asyncio.TimeoutError:
            print("Amazon Playwright scraping timed out")
            try:
                await browser.close()
            except:
                pass
            return {'reviews': [], 'title': None, 'price': None, 'description': None, 'source': 'amazon_playwright', 'error': 'timeout'}
        except Exception as e:
            print(f"Error scraping Amazon with Playwright: {e}")
            try:
                await browser.close()
            except:
                pass
            return {'reviews': [], 'title': None, 'price': None, 'description': None, 'source': 'amazon_playwright', 'error': str(e)}

async def scrape_flipkart_reviews(url: str, max_reviews: int = 10) -> Dict:
    """Scrape Flipkart reviews using Playwright"""
    print(f"Scraping Flipkart reviews from: {url}")
    
    FLIPKART_REVIEW_XPATHS = [
        "//div[contains(@class, 't-ZTKy') or contains(@class, '_6K-7Co')]",
        "//*[text()='Ratings & Reviews']/../..//div[contains(@class, 'ZmyHeo')]",
        "//div[div[contains(., 'Certified Buyer')]]/div[1]"
    ]
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            page.set_default_timeout(60000)
            await page.goto(url, wait_until="domcontentloaded")
            
            # Scroll to load reviews
            for i in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)
            
            # Extract title
            title = None
            title_selectors = [
                "//span[contains(@class,'B_NuCI')]",
                "//h1[contains(@class,'yhB1nd')]", 
                "//span[contains(@class,'VU-ZEz')]"
            ]
            
            for selector in title_selectors:
                try:
                    title_element = await page.query_selector(f"xpath={selector}")
                    if title_element:
                        title = await title_element.inner_text()
                        break
                except:
                    continue
            
            # Extract reviews
            reviews = []
            for i, xpath in enumerate(FLIPKART_REVIEW_XPATHS, 1):
                try:
                    print(f"Trying Flipkart review selector #{i}")
                    elements = await page.query_selector_all(f"xpath={xpath}")
                    
                    if elements:
                        print(f"Flipkart selector #{i} found {len(elements)} elements")
                        for element in elements[:max_reviews]:
                            try:
                                review_text = await element.inner_text()
                                if review_text and len(review_text.strip()) > 10:
                                    reviews.append(review_text.strip())
                            except:
                                continue
                        
                        if reviews:
                            print(f"Success! Found {len(reviews)} Flipkart reviews with selector #{i}")
                            break
                except Exception as e:
                    print(f"Error with Flipkart selector #{i}: {e}")
                    continue
            
            # Extract price
            price = None
            try:
                price_element = await page.query_selector("//div[contains(@class, '_30jeq3')]")
                if price_element:
                    price_text = await price_element.inner_text()
                    price_digits = re.sub(r'[^\d.]', '', price_text)
                    if price_digits:
                        price = float(price_digits)
            except:
                pass
            
            # Extract description  
            description = None
            desc_selectors = [
                "//div[text()='Description']/following::div[1]",
                "//div[contains(@class,'_1AN87F')]/div",
                "//div[text()='Highlights']/following::ul[1]"
            ]
            
            for selector in desc_selectors:
                try:
                    desc_element = await page.query_selector(f"xpath={selector}")
                    if desc_element:
                        description = await desc_element.inner_text()
                        if description:
                            description = description.strip()[:2000]
                            break
                except:
                    continue
            
            await browser.close()
            
            return {
                'reviews': reviews,
                'title': title,
                'price': price,
                'description': description,
                'source': 'flipkart'
            }
            
        except Exception as e:
            print(f"Error scraping Flipkart: {e}")
            try:
                await browser.close()
            except:
                pass
            return {'reviews': [], 'title': None, 'price': None, 'description': None, 'source': 'flipkart', 'error': str(e)}

def _cache_reviews(url: str, reviews: list):
    """Cache reviews to database"""
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
    """Cache price to database"""
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

async def scrape_data_enhanced(url: str) -> Dict:
    """Enhanced main scraping function"""
    init_db()
    
    print(f"Starting enhanced scraping for: {url}")
    
    if 'amazon' in url:
        result = await scrape_amazon_reviews_enhanced(url)
    elif 'flipkart.com' in url:
        result = await scrape_flipkart_reviews(url)
    else:
        print(f"Unsupported platform for URL: {url}")
        return {'reviews': [], 'title': None, 'price': None, 'description': None, 'error': 'unsupported_platform'}
    
    # Cache successful results
    if result.get('reviews'):
        _cache_reviews(url, result['reviews'])
    if result.get('price'):
        _cache_price(url, result['price'])
    
    return result

# Sync wrapper for backward compatibility
def scrape_data(url: str) -> Dict:
    """Sync wrapper for the enhanced async scraper"""
    return asyncio.run(scrape_data_enhanced(url))

if __name__ == '__main__':
    # Test URLs
    amazon_url = 'https://www.amazon.in/dp/B0DGTTPPT2'
    flipkart_url = 'https://www.flipkart.com/google-pixel-7a-sea-128-gb/p/itm8577377a36c72'
    
    print("--- Testing Enhanced Amazon Scraper ---")
    amazon_data = scrape_data(amazon_url)
    print(f"Amazon result: {len(amazon_data.get('reviews', []))} reviews, title: {amazon_data.get('title', 'None')}")
    
    print("\n--- Testing Enhanced Flipkart Scraper ---")
    flipkart_data = scrape_data(flipkart_url)
    print(f"Flipkart result: {len(flipkart_data.get('reviews', []))} reviews, title: {flipkart_data.get('title', 'None')}")