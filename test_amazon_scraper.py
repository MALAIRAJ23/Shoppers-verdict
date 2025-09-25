#!/usr/bin/env python3
"""
Quick test script for Amazon scraping
"""

from scraper import scrape_data
import sys

def test_amazon_scraping():
    print("Testing Amazon scraping...")
    
    test_url = 'https://www.amazon.in/Samsung-Galaxy-M35-5G-Moonlight/dp/B0D6Q7ZM8Z'
    print(f"URL: {test_url}")
    
    try:
        result = scrape_data(test_url)
        
        if result:
            print(f"✅ Success!")
            print(f"Title: {result.get('title', 'No title')}")
            print(f"Reviews found: {len(result.get('reviews', []))}")
            print(f"Price: {result.get('price_history', [{}])[-1].get('price', 'No price') if result.get('price_history') else 'No price'}")
            
            if result.get('reviews'):
                print(f"First review: {result['reviews'][0][:100]}...")
            else:
                print("No reviews found")
                
        else:
            print("❌ Failed - No result returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_amazon_scraping()