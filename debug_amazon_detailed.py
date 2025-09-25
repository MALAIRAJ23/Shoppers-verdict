#!/usr/bin/env python3
"""
Detailed Amazon scraping debug script
"""

from playwright.sync_api import sync_playwright
import time

def debug_amazon_page(url='https://www.amazon.in/dp/B0DGTTPPT2'):
    print(f"🔍 Debugging Amazon page: {url}")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=False)  # Show browser for debugging
            page = browser.new_page()
            
            print("📡 Loading page...")
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for page to fully load
            time.sleep(3)
            
            # Check if it's actually a product page
            title_selectors = [
                "#productTitle",
                "h1#title", 
                ".product-title",
                "h1"
            ]
            
            title_found = False
            for selector in title_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        title = element.inner_text().strip()
                        print(f"✅ Found title: {title[:50]}...")
                        title_found = True
                        break
                except:
                    continue
            
            if not title_found:
                print("❌ No title found - might not be a valid product page")
                
            # Look for review sections
            print("\n🔍 Looking for review sections...")
            review_indicators = [
                "[data-hook='reviews-block']",
                ".reviews-block",  
                "#reviews",
                ".customerReviews",
                "[data-hook='review-body']",
                ".review-text",
                ".cr-original-review-text"
            ]
            
            for indicator in review_indicators:
                elements = page.query_selector_all(indicator)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {indicator}")
                else:
                    print(f"❌ No elements found with: {indicator}")
            
            # Look for any text that might be reviews
            print("\n🔍 Searching for review-like content...")
            all_spans = page.query_selector_all("span")
            review_like_content = []
            
            for span in all_spans[:50]:  # Check first 50 spans
                try:
                    text = span.inner_text().strip()
                    if (len(text) > 30 and len(text) < 300 and 
                        any(word in text.lower() for word in ['good', 'bad', 'product', 'quality', 'excellent', 'poor', 'love', 'recommend'])):
                        review_like_content.append(text[:100] + "...")
                        if len(review_like_content) >= 5:
                            break
                except:
                    continue
            
            if review_like_content:
                print(f"✅ Found {len(review_like_content)} potential review texts:")
                for i, text in enumerate(review_like_content):
                    print(f"  {i+1}. {text}")
            else:
                print("❌ No review-like content found")
            
            # Check if we can find customer reviews section
            print("\n🔍 Looking for customer reviews link...")
            review_links = page.query_selector_all("a[href*='customer-reviews'], a[href*='#customerReviews'], [data-hook='see-all-reviews-link']")
            if review_links:
                print(f"✅ Found {len(review_links)} review links")
                for i, link in enumerate(review_links):
                    try:
                        href = link.get_attribute('href')
                        text = link.inner_text().strip()
                        print(f"  {i+1}. {text} -> {href}")
                    except:
                        continue
            else:
                print("❌ No review links found")
                
            input("\n⏸️  Press Enter to close browser...")
            browser.close()
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    # Test with the failing URL
    debug_amazon_page()