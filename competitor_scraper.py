"""
Competitor Product Scraper for Shopper's Verdict
Discovers and scrapes similar/competitor products for recommendations
"""

import re
import time
import random
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import requests
from bs4 import BeautifulSoup

class CompetitorScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def extract_search_keywords(self, title: str, description: str) -> List[str]:
        """Extract relevant search keywords from product title and description."""
        # Combine title and description
        text = f"{title} {description}".lower()
        
        # Remove common e-commerce terms
        exclude_terms = {
            'buy', 'online', 'shopping', 'store', 'sale', 'offer', 'deal', 
            'discount', 'price', 'rupees', 'rs', 'inr', 'free', 'delivery',
            'shipping', 'amazon', 'flipkart', 'product', 'item'
        }
        
        # Extract brand names (typically at the beginning)
        words = text.split()
        brand = words[0] if words else ""
        
        # Extract key product features
        keywords = []
        
        # Add brand if it looks like a brand name (capitalized, not common word)
        if brand and brand[0].isupper() and len(brand) > 2:
            keywords.append(brand)
        
        # Extract technical specs and features
        # Look for patterns like "128GB", "6.1 inch", "Android", etc.
        tech_patterns = [
            r'\d+gb\b', r'\d+mb\b', r'\d+tb\b',  # Storage
            r'\d+\.?\d*\s*inch\b', r'\d+\.?\d*"\b',  # Screen size
            r'\d+mp\b', r'\d+megapixel\b',  # Camera
            r'\d+mah\b',  # Battery
            r'\d+hz\b',  # Refresh rate
            r'\d+w\b', r'\d+watt\b',  # Power
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text)
            keywords.extend(matches)
        
        # Extract important nouns (potential product features)
        # Simple extraction - could be enhanced with NLP
        feature_words = []
        for word in words:
            if (len(word) > 3 and 
                word not in exclude_terms and 
                word.isalpha() and
                not word in ['with', 'from', 'this', 'that', 'have', 'been']):
                feature_words.append(word)
        
        # Take top important words
        keywords.extend(feature_words[:5])
        
        # Remove duplicates and clean
        keywords = list(set([k.strip() for k in keywords if k.strip()]))
        
        return keywords[:8]  # Limit to top 8 keywords
    
    def search_amazon_products(self, keywords: List[str], limit: int = 10) -> List[Dict]:
        """Search for products on Amazon using keywords."""
        products = []
        
        try:
            search_query = ' '.join(keywords[:3])  # Use top 3 keywords
            base_url = "https://www.amazon.in/s"
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # Search URL
                search_url = f"{base_url}?k={search_query.replace(' ', '+')}&ref=sr_pg_1"
                page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                
                # Wait for results to load
                page.wait_for_selector('[data-component-type="s-search-result"]', timeout=10000)
                
                # Extract product information
                products_found = 0
                results = page.query_selector_all('[data-component-type="s-search-result"]')
                
                for result in results[:limit]:
                    if products_found >= limit:
                        break
                    
                    try:
                        # Extract title
                        title_elem = result.query_selector('h2 a span, h2 span')
                        title = title_elem.inner_text().strip() if title_elem else ""
                        
                        # Extract URL
                        link_elem = result.query_selector('h2 a')
                        relative_url = link_elem.get_attribute('href') if link_elem else ""
                        full_url = urljoin("https://www.amazon.in", relative_url) if relative_url else ""
                        
                        # Extract price
                        price_elem = result.query_selector('.a-price-whole, .a-offscreen')
                        price_text = price_elem.inner_text() if price_elem else ""
                        price = self.extract_price_from_text(price_text)
                        
                        # Extract rating
                        rating_elem = result.query_selector('.a-icon-alt')
                        rating_text = rating_elem.get_attribute('aria-label') if rating_elem else ""
                        rating = self.extract_rating_from_text(rating_text)
                        
                        # Extract image
                        img_elem = result.query_selector('img')
                        image_url = img_elem.get_attribute('src') if img_elem else ""
                        
                        if title and full_url and '/dp/' in full_url:
                            products.append({
                                'title': title[:100],  # Truncate long titles
                                'url': full_url,
                                'price': price,
                                'rating': rating,
                                'image': image_url,
                                'site': 'amazon',
                                'source': 'search'
                            })
                            products_found += 1
                    
                    except Exception as e:
                        print(f"Error extracting Amazon product: {e}")
                        continue
                
                browser.close()
                
        except Exception as e:
            print(f"Error searching Amazon: {e}")
        
        return products
    
    def search_flipkart_products(self, keywords: List[str], limit: int = 10) -> List[Dict]:
        """Search for products on Flipkart using keywords."""
        products = []
        
        try:
            search_query = ' '.join(keywords[:3])
            base_url = "https://www.flipkart.com/search"
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # Search URL
                search_url = f"{base_url}?q={search_query.replace(' ', '%20')}"
                page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                
                # Wait for results
                page.wait_for_selector('[data-id]', timeout=10000)
                
                # Extract product information
                products_found = 0
                results = page.query_selector_all('[data-id]')
                
                for result in results[:limit]:
                    if products_found >= limit:
                        break
                    
                    try:
                        # Extract title
                        title_elem = result.query_selector('a[title], .s1Q9rs, ._4rR01T')
                        title = ""
                        if title_elem:
                            title = title_elem.get_attribute('title') or title_elem.inner_text()
                        title = title.strip() if title else ""
                        
                        # Extract URL
                        link_elem = result.query_selector('a[href*="/p/"]')
                        relative_url = link_elem.get_attribute('href') if link_elem else ""
                        full_url = urljoin("https://www.flipkart.com", relative_url) if relative_url else ""
                        
                        # Extract price
                        price_elem = result.query_selector('._30jeq3, ._1_WHN1')
                        price_text = price_elem.inner_text() if price_elem else ""
                        price = self.extract_price_from_text(price_text)
                        
                        # Extract rating
                        rating_elem = result.query_selector('.XQDdHH, ._3LWZlK')
                        rating_text = rating_elem.inner_text() if rating_elem else ""
                        rating = self.extract_rating_from_text(rating_text)
                        
                        # Extract image
                        img_elem = result.query_selector('img')
                        image_url = img_elem.get_attribute('src') if img_elem else ""
                        
                        if title and full_url and '/p/' in full_url:
                            products.append({
                                'title': title[:100],
                                'url': full_url,
                                'price': price,
                                'rating': rating,
                                'image': image_url,
                                'site': 'flipkart',
                                'source': 'search'
                            })
                            products_found += 1
                    
                    except Exception as e:
                        print(f"Error extracting Flipkart product: {e}")
                        continue
                
                browser.close()
                
        except Exception as e:
            print(f"Error searching Flipkart: {e}")
        
        return products
    
    def get_related_products_from_page(self, product_url: str) -> List[Dict]:
        """Extract related/similar products from the current product page."""
        products = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
                
                if 'amazon' in product_url.lower():
                    products = self._extract_amazon_related_products(page)
                elif 'flipkart' in product_url.lower():
                    products = self._extract_flipkart_related_products(page)
                
                browser.close()
                
        except Exception as e:
            print(f"Error getting related products: {e}")
        
        return products
    
    def _extract_amazon_related_products(self, page) -> List[Dict]:
        """Extract related products from Amazon product page."""
        products = []
        
        try:
            # Look for various related product sections
            selectors = [
                '#similarities_feature_div a[href*="/dp/"]',  # Similar items
                '#HLCXComparisonWidget a[href*="/dp/"]',     # Comparison widget
                '#rhf a[href*="/dp/"]',                      # Related products
                '[data-a-carousel-options] a[href*="/dp/"]', # Carousel items
            ]
            
            for selector in selectors:
                try:
                    related_links = page.query_selector_all(selector)
                    
                    for link in related_links[:5]:  # Limit per section
                        href = link.get_attribute('href')
                        if href and '/dp/' in href:
                            # Extract product info
                            title_elem = link.query_selector('img, span')
                            title = ""
                            if title_elem:
                                title = (title_elem.get_attribute('alt') or 
                                        title_elem.get_attribute('aria-label') or 
                                        title_elem.inner_text()).strip()
                            
                            if title:
                                full_url = urljoin("https://www.amazon.in", href)
                                products.append({
                                    'title': title[:100],
                                    'url': full_url,
                                    'site': 'amazon',
                                    'source': 'related'
                                })
                                
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Error extracting Amazon related products: {e}")
        
        return products
    
    def _extract_flipkart_related_products(self, page) -> List[Dict]:
        """Extract related products from Flipkart product page."""
        products = []
        
        try:
            # Look for related product sections
            selectors = [
                'a[href*="/p/"]',  # General product links
            ]
            
            for selector in selectors:
                try:
                    related_links = page.query_selector_all(selector)
                    
                    for link in related_links[:10]:  # Check more links
                        href = link.get_attribute('href')
                        if href and '/p/' in href and href != page.url:
                            # Extract title from link text or nearby elements
                            title = link.inner_text().strip()
                            if not title:
                                # Try to get title from nearby text or image alt
                                img = link.query_selector('img')
                                if img:
                                    title = img.get_attribute('alt') or ""
                            
                            if title and len(title) > 10:  # Valid title
                                full_url = urljoin("https://www.flipkart.com", href)
                                products.append({
                                    'title': title[:100],
                                    'url': full_url,
                                    'site': 'flipkart',
                                    'source': 'related'
                                })
                                
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Error extracting Flipkart related products: {e}")
        
        return products
    
    def extract_price_from_text(self, price_text: str) -> Optional[float]:
        """Extract numeric price from price text."""
        if not price_text:
            return None
        
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[₹,\s]', '', price_text)
            # Extract numbers
            numbers = re.findall(r'\d+\.?\d*', cleaned)
            if numbers:
                return float(numbers[0])
        except Exception:
            pass
        
        return None
    
    def extract_rating_from_text(self, rating_text: str) -> Optional[float]:
        """Extract numeric rating from rating text."""
        if not rating_text:
            return None
        
        try:
            # Look for patterns like "4.5 out of 5" or "4.5"
            numbers = re.findall(r'\d+\.?\d*', rating_text)
            if numbers:
                rating = float(numbers[0])
                return rating if 0 <= rating <= 5 else None
        except Exception:
            pass
        
        return None
    
    def discover_competitors(self, product_url: str, title: str, description: str, 
                           max_results: int = 15) -> List[Dict]:
        """
        Main method to discover competitor products.
        
        Args:
            product_url: URL of the base product
            title: Product title
            description: Product description
            max_results: Maximum number of competitors to return
        
        Returns:
            List of competitor product dictionaries
        """
        all_competitors = []
        
        try:
            # Extract search keywords
            keywords = self.extract_search_keywords(title, description)
            print(f"Search keywords: {keywords}")
            
            # Get related products from the same page
            related_products = self.get_related_products_from_page(product_url)
            all_competitors.extend(related_products)
            
            # Search both platforms for similar products
            if 'amazon' not in product_url.lower():
                amazon_products = self.search_amazon_products(keywords, limit=8)
                all_competitors.extend(amazon_products)
            
            if 'flipkart' not in product_url.lower():
                flipkart_products = self.search_flipkart_products(keywords, limit=8)
                all_competitors.extend(flipkart_products)
            
            # Remove duplicates and filter
            seen_urls = set()
            unique_competitors = []
            
            for product in all_competitors:
                url = product.get('url', '')
                if url and url not in seen_urls and url != product_url:
                    seen_urls.add(url)
                    unique_competitors.append(product)
            
            # Limit results
            return unique_competitors[:max_results]
            
        except Exception as e:
            print(f"Error discovering competitors: {e}")
            return []

# Global instance
competitor_scraper = CompetitorScraper()

def get_competitor_products(product_url: str, title: str, description: str, 
                          max_results: int = 10) -> List[Dict]:
    """
    Public function to get competitor products.
    
    Args:
        product_url: URL of the product to find competitors for
        title: Product title
        description: Product description
        max_results: Maximum number of competitors to return
    
    Returns:
        List of competitor product dictionaries
    """
    return competitor_scraper.discover_competitors(
        product_url, title, description, max_results
    )

if __name__ == '__main__':
    # Test the competitor scraper
    test_url = 'https://www.flipkart.com/google-pixel-7a-sea-128-gb/p/itm8577377a36c72'
    test_title = 'Google Pixel 7a (Sea, 128 GB)'
    test_description = 'Google Pixel 7a smartphone with 128GB storage and advanced camera features'
    
    print("Testing competitor scraper...")
    competitors = get_competitor_products(test_url, test_title, test_description, 5)
    
    print(f"Found {len(competitors)} competitor products:")
    for i, comp in enumerate(competitors, 1):
        print(f"{i}. {comp['title']} ({comp['site']}) - Source: {comp['source']}")
        if comp.get('price'):
            print(f"   Price: ₹{comp['price']}")
        print(f"   URL: {comp['url']}\n")